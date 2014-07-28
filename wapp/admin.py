
from flask_peewee.admin import Admin, ModelAdmin

from app import app, db
from auth import auth
from models import User, Location, Acl
from pbkdf2 import hashing_passwords as hp

admin = Admin(app, auth, branding='ownTracks')

# Check for existing admin user and in none
# exists create one
# TODO: Show flash message for newly created
# admin user
try:
    test_admin = User.get(User.username == 'admin')
except: 
    # No Admin user yet, so create one
    test_admin = auth.User(username='admin', email='', admin=True, active=True, superuser=True)
    test_admin.set_password('admin')
    test_admin.save()

# or you could admin.register(User, ModelAdmin) -- you would also register
# any other models here.

class LocationAdmin(ModelAdmin):
    columns = ('tst', 'username', 'device', 'lat', 'lon', )

class UserAdmin(ModelAdmin):
    columns = ('username', 'superuser', 'pbkdf2',)

    # Upon saving the User model in admin, set the PBKDF2 hash for
    # the password

    def save_model(self, instance, form, adding=False):
        orig_password = instance.password
        user = super(UserAdmin, self).save_model(instance, form, adding)
        if orig_password != form.password.data:
                user.set_password(form.password.data)
        user.save()
        
    # 
    #     pbkdf2 = hp.make_hash(instance.password)
    #     print "***** ", instance.password, pbkdf2
    #     print "----- ", orig_password, form.password.data
    # 
    #     user = super(UserAdmin, self).save_model(instance, form, adding)
    # 
    #     user.pbkdf2 = pbkdf2
    # 
        return user

class AclAdmin(ModelAdmin):
    columns = ('user', 'topic', 'rw',)
    foreign_key_lookups = {'user': 'username'}
    filter_fields = ('user', 'topic', 'rw', 'user__username')
    exclude = ('user__password', )

auth.register_admin(admin)
admin.register(User, UserAdmin)
admin.register(Location, LocationAdmin)
admin.register(Acl, AclAdmin)
