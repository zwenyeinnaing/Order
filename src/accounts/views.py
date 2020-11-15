from django.forms import inlineformset_factory
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .form import OrderForm,CustomerForm,CreateUserForm
from .models import *
from .filters import OrderFilter
from .decorators import unauthenticated_user,allowed_users,admin_only


# Create your views here.

@unauthenticated_user
def registerPage(request):
   
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # group = Group.objects.get(name='customer')
            # user.groups.add(group)
            # Customer.objects.create(
            #     user=user,
            # )

            messages.success(request,'Account was create for '+ username)
            return redirect('login')
    context = {'form':form}
    return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginPage(request):
  
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request,'Username or password is incorrect')

    context={}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    ords = request.user.customer.order_set.all()
    cus = request.user.customer.id
    customers = Customer.objects.all()
    total_customers = customers.count()
    delivered   = ords.filter(status='Delivered').count()
    pending     = ords.filter(status='Pending').count()
    total_ords  = ords.count()
    last_ords   = total_ords - delivered
    total_ords  = ords.count()
    
    context = {
        'ords': ords,
        'total_customers' : total_customers,
        'delivered' : delivered,
        'pending'   : pending,
        'last_ords' : last_ords,
        'cus'   : cus,
        }
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()

# def accountSettings(request):
# 	customer = request.user.customer
# 	form = CustomerForm(instance=customer)

# 	if request.method == 'POST':
# 		form = CustomerForm(request.POST, request.FILES,instance=customer)
# 		if form.is_valid():
# 			form.save()


# 	context = {'form':form}
# 	return render(request, 'accounts/account_setting.html', context)

    context = {'form':form}
    return render(request, 'accounts/account_setting.html',context)

@login_required(login_url='login')
@admin_only
def home(request):
    customers = Customer.objects.all()
    ords        = Order.objects.all()
    # orders    = Order.objects.all()
    total_customers = customers.count()
    total_ords  = ords.count()
    # total_orders = orders.count()
    delivered   = ords.filter(status='Delivered').count()
    # delivered = orders.filter(status='Delivered').count()
    pending     = ords.filter(status='Pending').count()
    # pending = orders.filter(status='Pending').count()
    # outfor_delivery = orders.filter(status='Out for delivery').count()
    last_ords   = total_ords - delivered
    # ord         = Order.objects.get(id=)
    # ord_customer = ord.customer.name


    context  = {
        'ords' : ords,
        'customers' : customers,
        'total_customers' : total_customers,
        'total_ords'  : total_ords,
        'delivered' : delivered,
        'pending'   : pending,
        'last_ords' : last_ords,
        # 'ord_customer' : ord_customer,
        # 'outfor_delivery' : outfor_delivery,
    }
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createCustomer(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form' : form}
    return render(request,'accounts/create_customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateCustomer(request,pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)
    if  request.method == 'POST':
        # print('Printing POST',request.POST,)
        form = CustomerForm(request.POST,instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request,'accounts/update_customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()
    total = 0 
    myFilter = OrderFilter(request.GET,queryset=orders)
    orders = myFilter.qs
    for name in orders:
        product = Product.objects.get(name=name)
        cost = product.price
        total += cost 
    context = {'customer' : customer,'orders' : orders,'order_count' : order_count,'myFilter': myFilter,'total': total}
    return render(request,'accounts/customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    context     = {
        'products' : products
    }
    return render(request,'accounts/products.html',context)

@login_required(login_url='login')
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5 )
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		#print('Printing POST:', request.POST)
		form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'form':formset}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	print('ORDER:', order)
	if request.method == 'POST':

		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'accounts/update_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if  request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item':order}
    return render(request,'accounts/delete.html',context)

