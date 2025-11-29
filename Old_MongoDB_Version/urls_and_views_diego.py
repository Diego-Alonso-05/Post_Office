#new urls

path('warehouses/', views.warehouses_list, name='warehouses_list'),
path('warehouses/create/', views.warehouses_create, name='warehouses_create'),
path('warehouses/edit/<str:warehouse_id>/', views.warehouses_edit, name='warehouses_edit'),
path('warehouses/delete/<str:warehouse_id>/', views.warehouses_delete, name='warehouses_delete'),


path('profile/', views.client_profile, name='client_profile'),


#views_diego
#Werehouse form and views
class WarehouseForm(forms.Form):
    name = forms.CharField(max_length=100)
    contact = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    opening_time = forms.TimeField()
    closing_time = forms.TimeField()
    maximum_storage = forms.IntegerField()

# Views
@login_required
@role_required(["admin"])
def warehouses_list(request):
    all_warehouses = list(postoffice.find())
    for w in all_warehouses:
        w['id'] = str(w['_id'])
    return render(request, "warehouses/list.html", {"warehouses": all_warehouses})

@login_required
@role_required(["admin"])
def warehouses_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            data['opening_time'] = data['opening_time'].strftime("%H:%M")
            data['closing_time'] = data['closing_time'].strftime("%H:%M")
            postoffice.insert_one(data)
            return redirect("warehouses_list")
    else:
        form = WarehouseForm()
    return render(request, "warehouses/create.html", {"form": form})

@login_required
@role_required(["admin"])
def warehouses_edit(request, warehouse_id):
    warehouse = postoffice.find_one({"_id": ObjectId(warehouse_id)})
    if not warehouse:
        return redirect("warehouses_list")

    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            data['opening_time'] = data['opening_time'].strftime("%H:%M")
            data['closing_time'] = data['closing_time'].strftime("%H:%M")
            postoffice.update_one({"_id": ObjectId(warehouse_id)}, {"$set": data})
            return redirect("warehouses_list")
    else:
        if 'opening_time' in warehouse:
            warehouse['opening_time'] = datetime.strptime(warehouse['opening_time'], "%H:%M").time()
        if 'closing_time' in warehouse:
            warehouse['closing_time'] = datetime.strptime(warehouse['closing_time'], "%H:%M").time()
        form = WarehouseForm(initial=warehouse)

    warehouse['id'] = str(warehouse['_id'])
    return render(request, "warehouses/edit.html", {"form": form, "warehouse_id": warehouse['id']})

@login_required
@role_required(["admin"])
def warehouses_delete(request, warehouse_id):
    postoffice.delete_one({"_id": ObjectId(warehouse_id)})
    return redirect("warehouses_list")



# Client Profile 
@login_required
@role_required(["client", "admin"])
def client_profile(request):
    user_doc = users.find_one({"username": request.user.username})
    if not user_doc:
        return redirect("dashboard")

    client_deliveries = list(deliveries.find({"client_id": user_doc["_id"]}))
    client_deliveries.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
    for d in client_deliveries:
        d['id'] = str(d['_id'])

    client_invoices = list(invoices.find({"client_id": user_doc["_id"]}))
    client_invoices.sort(key=lambda x: x.get("invoice_datetime", datetime.min), reverse=True)
    for i in client_invoices:
        i['id'] = str(i['_id'])

    return render(request, "clients/profile.html", {
        "user": user_doc,               
        "deliveries": client_deliveries,
        "invoices": client_invoices    
    })

