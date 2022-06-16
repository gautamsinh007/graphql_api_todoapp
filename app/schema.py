from dataclasses import field
from lib2to3.pgen2 import token
from pickle import TRUE

from urllib import request, response
import graphene
from  django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from graphene_django import DjangoObjectType
# from  .models import Category, Ingredient
from graphql_auth.schema import UserQuery,MeQuery 
from graphql_auth import mutations    
# from django.contrib.auth.decorators import login_required
from graphql_jwt.decorators import login_required
from .models import *
from graphql_jwt.shortcuts import create_refresh_token, get_token


def authenticate_role(func):
    def wrap(self,info,**kwargs):
        auth_header = info.context.META.get('HTTP_AUTHORIZATION')
        if auth_header is None:
            raise Exception('auth Token not providedd')
        else:
            new_token=auth_header.replace("JWT","").replace(" ","")
            if TokenAdd.objects.filter(token=new_token).exists():
                return func(self,info,**kwargs)
            raise Exception("Please Login Again you'r logged out!!!!")
    return wrap


class  UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account  = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    revoke_token = mutations.RevokeToken.Field()


class Tokentype(DjangoObjectType):
    class Meta:
        model = TokenAdd
        fields = ("token","user")


class Todotype(DjangoObjectType):
    class Meta:
        model = TodoAdd
        user=get_user_model()
        fields =['id','task','user',"datetime"]




class loginuser(graphene.Mutation):
    class Arguments:
        username=graphene.String(required=True)
        password=graphene.String(required=True)
    token = graphene.Field(Tokentype)
    msg=graphene.String()
    def mutate(self,info,username,password):
        # token=''
        # if not get_user_model().objects.filter(username=username).exists():
        #     return storeToken(token=None, msg="invalid username")
        valid_user = authenticate(username=username,password=password)
        if valid_user:
            user_obj=get_user_model().objects.get(username=username)
            if get_user_model().objects.filter(id=user_obj.id).exists():
                if TokenAdd.objects.filter(user=user_obj.id).exists():
                    token_obj=TokenAdd.objects.get(user=user_obj.id)
                 
                    return loginuser(token=token_obj,)
                else:
                    user = get_user_model().objects.get(id=user_obj.id)
                    token = get_token(user)
                    token_obj=TokenAdd(token=token,user=user)
                    token_obj.save()
                    # return "gaaaya adjshdksdjsjd"
                    return loginuser(token=token_obj)
            else:
                raise Exception('User ID not exits!!!!')
        else:
            return loginuser(token=None,msg="Invalid Credentials")



class Logout(graphene.Mutation):
    class Arguments:
        id=graphene.ID()
    msg = graphene.String()

    @staticmethod
    def mutate(root,info,id):
        obj=TokenAdd.objects.get(user=id)
        obj.delete()
        msg='succfully logout'
        return Logout(msg=msg)











class  todos_add(graphene.Mutation):
    class Arguments:
        user  = graphene.Int()
        task = graphene.String()
        
    todoadd = graphene.Field(Todotype)
    
    @classmethod
    def mutate(cls, root , info , user, task):
       todoadd = TodoAdd(task=task, user=get_user_model().objects.get(id=user))
       todoadd.save() 
       return  todos_add(todoadd=todoadd)


class todo_delete(graphene.Mutation):
    class Arguments:
      id = graphene.ID()
    msg = graphene.String()
    @classmethod
    def mutate(cls,root, info, id):
        print(id, "<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        todos_delete =TodoAdd.objects.get(id=id)
        print(todos_delete,"?????????????????????????")
        todos_delete.delete()
        msg = "deleet ho gaya "
        return todo_delete(msg=msg)

      

        
class todo_upadte(graphene.Mutation):
    class Arguments:
        id_post = graphene.ID()
        task  = graphene.String()
    
    todos_update = graphene.Field(Todotype)
    
    @staticmethod
    def mutate(root,info,id_post,task):
        user = info.context.user
        print("enter",user)
        to_do = TodoAdd.objects.get(id=id_post)
        print(to_do,"@@@@@@@@@")
        to_do.task = task
        to_do.save() 
        return todo_upadte(todos_update=to_do)
    
    
    
    
class Mutation(AuthMutation,graphene.ObjectType):
    toodadd = todos_add.Field()
    tododelete = todo_delete.Field()
    todoupdate = todo_upadte.Field()
    login = loginuser.Field()    
    logout = Logout.Field()

class Query(UserQuery,MeQuery,graphene.ObjectType):
    
    all_user = graphene.List(UserType)
    all_todo = graphene.List(Todotype)
    todo_by_id=graphene.Field(Todotype,id=graphene.ID())
    
    todo_get = graphene.List(Todotype,id=graphene.ID())
    id = graphene.ID
    
    def resolve_all_user(root,info):
        return get_user_model().objects.all()
        
    def resolve_all_todo(root,info):
        return TodoAdd.objects.all()
    
    
    def  resolve_todo_by_id(root, info,id):
       return  TodoAdd.objects.get(id=id)
    
    
    def resolve_todo_get(root, info,id):
        return  TodoAdd.objects.filter(user=id)
        
   
        

schema = graphene.Schema(query=Query,mutation=Mutation)  #  this is form mutation class  
