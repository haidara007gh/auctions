from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("dashboard/<str:username>",views.dashboard, name="dashboard"),
    path("profile/<str:username>", views.profile, name = "profile"),
    path("category/<str:category>", views.category, name="category"),
    path("create", views.create_listing_view, name="create_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name = "remove_from_watchlist"),
    path("placebid/<int:listing_id>", views.place_bid, name = "place_bid"),
    path("unbid/<int:bid_id>", views.unbid, name="unbid"),
    path("comment/<int:listing_id>", views.comment, name="comment"), 
    path("close_auction/<int:listing_id>", views.close_auction, name = "close_auction"),
    path("search", views.search, name="search")
] 


if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)