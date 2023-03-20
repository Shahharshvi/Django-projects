from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.http import HttpResponse
from .forms import *
from django.contrib.auth.decorators import login_required

import csv
# Create your views here.

def home(request):
    title="Welcome:This is Home page"
    context={"title":title,}
    # return render(request,'home.html',context)
    return redirect('/list_items')

@login_required
def list_items(request):
    form=StockSearchForm(request.POST or None)
    header='LIST OF ITEMS'
    queryset=Stock.objects.all()
    context={
          "form":form,   
        "header":header,
          "queryset":queryset,
             }
    if request.method=='POST':
        queryset=Stock.objects.filter(item_name__icontains=form['item_name'].value())
        if form['export_to_CSV'].value()==True:
            response=HttpResponse(content_type='text/csv')
            response['Content-Disposition']='attachment;filename="List of stock.csv"'
            writer=csv.writer(response)
            writer.writerow(['CATEGORY','ITEM NAME','QUANTITY'])
            instance=queryset
            for stock in instance:
                writer.writerow([stock.category,stock.item_name,stock.quantity])
                return response

    context={
        "form":form,
        "header":header,
          "queryset":queryset,   
             }
    return render(request,'list_items.html',context)

@login_required
def add_items(request):
    form=StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request,'Successfully inserted item')
        return redirect('/list_items')
    context={
        "form":form,
        "title":"Add Item",
    }
    return render(request,"add_items.html",context)

def update_items(request,pk):
    queryset=Stock.objects.get(id=pk)
    form=StockUpdateForm(instance=queryset)
    if request.method=='POST':
        form=StockUpdateForm(request.POST,instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request,'Successfully updated')
            return redirect('/list_items')
        
    context={
        'form':form
    }
    
    return render(request,'add_items.html',context)

def delete_items(request,pk):
    queryset=Stock.objects.get(id=pk)
    if request.method=='POST':
        queryset.delete()
        messages.success(request,'Successfully deleted')
        return redirect('/list_items')
    return render(request,'delete_items.html')

def stock_detail(request,pk):
    queryset=Stock.objects.get(id=pk)
    context={
        "queryset":queryset,
    }
    return render(request,"stock_detail.html",context)
    
def issue_items(request,pk):
    queryset=Stock.objects.get(id=pk)
    form=IssueForm(request.POST or None,instance=queryset)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.receive_quantity=0
        instance.quantity-=instance.issue_quantity
        instance.issue_by=str(request.user)
        messages.success(request,"Issued successfully. "+str(instance.quantity)+" "+str(instance.item_name)+"s now left in store")
        instance.save()
        return redirect('/stock_detail/'+str(instance.id))
        #return HTTpresponseRedirect(instance.get_absolute_url())
    context={
        "title":'Issue '+str(queryset.item_name),
        "queryset":queryset,
        "form":form,
        "username":'Issue By: '+str(request.user),
    }
    return render(request,"add_items.html",context)
        
def receive_items(request,pk):
    queryset=Stock.objects.get(id=pk)
    form=ReceiveForm(request.POST or None,instance=queryset)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.issue_quantity=0
        instance.quantity+=instance.receive_quantity
        instance.receive_by=str(request.user)
        instance.save()
        messages.success(request,"received successfully. "+str(instance.quantity)+" "+str(instance.item_name)+"s now left in store")
        return redirect('/stock_detail/'+str(instance.id))
        #return HTTpresponseRedirect(instance.get_absolute_url())
    context={
        "title":'receive '+str(queryset.item_name),
        "instance":queryset,
        "form":form,
        "username":'Receive By: '+str(request.user),
    }
    return render(request,"add_items.html",context)

def reorder_level(request,pk):
    queryset=Stock.objects.get(id=pk)
    form=ReorderLevelForm(request.POST or None,instance=queryset)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"Reorder level for "+str(instance.item_name)+"is updated to "+str(instance.reorder_level))

        return redirect('/list_items')
        #return HTTpresponseRedirect(instance.get_absolute_url())
    context={
        "instance":queryset,
        "form":form,
    }
    return render(request,"add_items.html",context)

@login_required
def list_history(request):
    form=StockHistorySearchForm(request.POST or None)
    header='HISTORY DATA'
    queryset=Stock.objects.all()
    context={
        "form":form,
          "header":header,
          "queryset":queryset, 
             }
    if request.method=='POST':
        category=form['category'].value()
        queryset=StockHistory.objects.filter(item_name__icontains=form['item_name'].value(),
            last_updated_range=[
                form['start_date'].value(),
                form['end_date'].value()
        ])
        if(category!=''):
            queryset=queryset.filter(category_id=category)
        if form['export_to_CSV'].value()==True:
            response=HttpResponse(content_type='text/csv')
            response['Content-Disposition']='attachment;filename="Stock History.csv"'
            writer=csv.writer(response)
            writer.writerow(['CATEGORY','ITEM NAME','QUANTITY','ISSUE QUANTITY','RECEIVE QUANTITY','RECEIVE BY','ISSUE BY','LAST UPDATED'])
            instance=queryset
            for stock in instance:
                writer.writerow([stock.category,stock.item_name,stock.quantity,stock.issue_quantity,stock.receive_quantity,stock.receive_by,stock.issue_by,stock.last_updated])
                return response
            context={
            "form":form,
          "header":header,
          "queryset":queryset, 
             }
    return render(request,"list_history.html",context)
                  