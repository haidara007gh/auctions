from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *
from datetime import datetime
from .forms import *



def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html",{
        'listings':listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Logged in successfully.')
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.ERROR, 'Invalid username and/or password.')
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.add_message(request,messages.INFO,'You are now logged out!')
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        messages.add_message(request, messages.SUCCESS, 'Account created successfully')
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def create_listing_view(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        print("Form validity: ", form.is_valid())
        if form.is_valid():
            user = User.objects.get(pk=request.user.id)
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            url = form.cleaned_data["url"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]
            
            listing = Listing(
                user = user,
                active=True,
                title=title,
                description=description,
                datetime=datetime.now(),
                url = url,
                price = price,
                category = category
            )
            
            listing.save()
            messages.add_message(request, messages.SUCCESS, 'You created a new listing')
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.add_message(request, messages.ERROR, 'Listing creation failed')
            return render(request, "auctions/new.html", {
                "form": form.as_p
            })

    return render(request, "auctions/create.html", {
        'form': NewListingForm().as_p
    }) 



def category(request, category):
    categories = []
    list = []
    if category == 'all':
        categories = Listing.objects.values_list('category', flat=True).distinct()
    listings = Listing.objects.raw("SELECT * from auctions_listing WHERE active = True and category LIKE %s ",['%'+category+'%'])
    
    return render(request,"auctions/categories.html",{
        "listings":listings,
        'categories':categories,
        'category': category.capitalize()
    })



def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.user.id and listing.user == User.objects.get(pk=request.user.id):
        user_created_listing = True
    else:
        user_created_listing= False
    
    
    number_of_bids = Bid.objects.filter(listing=listing_id).count()
    
    form_bid = NewBiddingForm()
    form_comment = NewCommentForm()
    
    #potential doesnotexist error if listing is not in watchlist
    #Purpose: we only want to add to watchlist when listing does not exist in watchlist
    try:
        watchlist = Watchlist.objects.get(listing=listing)
        watchlisted = True
    except ObjectDoesNotExist:
        watchlisted = False
    
    #potential doesnotexist error if there are no comments for the listing
    try:
        comments_queryset = Comment.objects.filter(listing=listing)
        comments = []
        for comment in comments_queryset:
            comments.append(comment)
    except ObjectDoesNotExist:
        comments = None
    
    return render(request, "auctions/listing.html",{
        'listing':listing, 
        'watchlisted':watchlisted, 
        'form_bid':form_bid, 'form_comment': form_comment, 
        'number_of_bids':number_of_bids,
        'comments':comments,
        'user_created_listing': user_created_listing
    })



@login_required()
def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlists = Watchlist.objects.filter(user = user)
    listings = []
    for watchlist in watchlists:
        listings.append(watchlist.listing)
    return render(request, 'auctions/watchlist.html',{
        'listings': listings, 'count':len(listings)
    })



@login_required()
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    
    try:
        #potential doesnotexist error if listing is not in watchlist
        #we want to only add to watchlist when listing does not exist in watchlist
        listing = Watchlist.objects.get(listing=listing) 
        
    except ObjectDoesNotExist:
        user = User.objects.get(pk=request.user.id)
        watchlist = Watchlist(listing=listing,user=user)
        watchlist.save()
        messages.success(request,'Added to watchlist')
    return HttpResponseRedirect(reverse('watchlist'))



@login_required()
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    Watchlist.objects.get(listing = listing).delete()
    messages.success(request,'Removed from watchlist')
    return HttpResponseRedirect(reverse('watchlist'))
    


@login_required()
def place_bid(request, listing_id):
    if request.method == "POST":
        form = NewBiddingForm(request.POST)
        listing = Listing.objects.get(pk=listing_id)
        bid_aggregate = Bid.objects.filter(listing=listing).aggregate(Max('price'))
        highest_bid = bid_aggregate['price__max']
        
        if form.is_valid():
            price = form.cleaned_data["price"]
            user = User.objects.get(pk=request.user.id)
            
            if highest_bid and price > highest_bid:   
                bid = Bid(listing=listing, user=user, price=price, datetime=datetime.now())
                bid.save()
                messages.add_message(request,messages.SUCCESS,'Bid was placed successfully.')
            elif highest_bid is None and price > listing.price:
                 bid = Bid(listing=listing, user=user, price=price, datetime=datetime.now())
                 bid.save()
                 messages.success(request, "Bid placed successfully")
            else:
                messages.add_message(request,messages.WARNING,'Cannot place bid PRICE too small.')
                return HttpResponseRedirect(reverse('listing',args=(listing_id,)))
        return HttpResponseRedirect(reverse('dashboard',args=(request.user)))
    


@login_required()
def unbid(request, bid_id):
    Bid.objects.get(pk=bid_id).delete()
    messages.success(request,'Removed bid')
    return HttpResponseRedirect(reverse('dashboard',args=(request.user,)))



@login_required()
def comment(request, listing_id):
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        listing = Listing.objects.get(pk=listing_id)
        user = User.objects.get(pk = request.user.id)
        if form.is_valid():
            message = form.cleaned_data["message"]
            comment = Comment(listing=listing, user=user, message=message, datetime=datetime.now())
            comment.save()
            messages.success(request,"You made a comment!")
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))



@login_required()
def close_auction(request, listing_id):
    
    listing = Listing.objects.get(pk=listing_id)

    bid_aggregate = Bid.objects.filter(listing=listing).aggregate(Max('price'))
    
    highest_bid_price = bid_aggregate['price__max']
    
    if highest_bid_price:
        highest_bid = Bid.objects.get(price=highest_bid_price)
        winner = highest_bid.user
        winner = Winner(user=winner, listing=listing, bid=highest_bid)
        winner.save()
    
    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse('dashboard',args=(request.user,)))



@login_required()
def dashboard(request, username):
    
    user = User.objects.get(pk=request.user.id)
    bids = Bid.objects.filter(user=user)
    active_listings = Listing.objects.filter(user=user,active=True)
    inactive_listings = Listing.objects.filter(user=user,active=False)
    winnings = Winner.objects.filter(user=user)
    closed_listings = {}
    
    for listing in inactive_listings:
        try:
            winner = Winner.objects.get(listing=listing)
            closed_listings[listing]= winner.user
        except:
            winner = None
            closed_listings[listing] = winner

    return render(request,'auctions/dashboard.html',
    {
        'user' : user,
        'bids':bids,
        'active_listings':active_listings,
        'closed_listings':closed_listings, 
        'winnings': winnings
    })



@login_required()
def profile(request,username):
    try:
        user = User.objects.get(username=username)
    except:
        user = None
    return render(request,'auctions/profile.html',{
        "user":user
    })


def search(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print(query)
        #"SELECT * from auctions_listing WHERE active = True and category LIKE %s ",['%'+category+'%']
        #listings = Listing.objects.raw("SELECT * FROM auctions_listing WHERE category LIKE %s or title LIKE %s", ['%'+query+'%'])
        listings = Listing.objects.raw("SELECT * from auctions_listing WHERE active = True \
                                        AND description LIKE %s OR title LIKE %s OR category LIKE %s",['%'+query+'%','%'+query+'%','%'+query+'%'])

        for listing in listings:
            print(listing)
        return render(request, 'auctions/search.html',{
            'listings':listings
        })


