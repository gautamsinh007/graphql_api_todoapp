
from flask import Flask, redirect , request,  url_for,session
from flask_restful import abort
from flask import Flask,render_template
import requests


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
url = 'http://127.0.0.1:8000/graphql'


#  ---------------------------------------   user Register ---------------------------------------



@app.route("/register",methods=['POST', 'GET'])
def register():

    if request.method=='POST':
       
        username=request.form['username']
        email=request.form['email']
        password1=request.form['password1']
        password2=request.form['password2']
        query ='''mutation{
        register(username:"%s",email:"%s",password1:"%s", password2:"%s"){
            success
            errors
             token
        }
        }''' % (username,email,password1,password2)
       
        
        response=requests.post(url=url,json={"query":query})
        print(response,"===========================")
        data=response.json()
    
        print(data,"================----------======================")
        if response.json()['data']['register'] is None:
            data=response.json()
            
            msg=data["errors"]
            return render_template("register.html",msg=msg)
        else:
            
            return redirect(url_for('login'))
        
    return render_template('register.html')




#  ---------------------------------------   user login ---------------------------------------


@app.route('/login' , methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form["password"]
        
        query = '''
             mutation{
  
            login(password:"%s", username:"%s") {
            token{
                user{
               
                id
                username
                }
            }
                msg
            }
            }''' %(password,username)    
                     
                     
        datas = requests.post(url=url,json={"query":query})
        
        print(datas,"============----------------------")
        if datas.json()['data']['login']['token'] is None:
            print(datas.json()["data"]['login']['token'])
            msg=datas.json()['data']['login']['msg']
            return render_template("login.html",msg=msg)
        else:
            session['token']=datas.json()['data']['login']['token']
            session['user_id'] = datas.json()['data']['login']['token']['user']['id']
            session['username'] = datas.json()['data']['login']['token']['user']['username']
          
            print(session['user_id'],"==============")
            print(session['token'],"==============")
            print(session['username'],"=============")
            return redirect(url_for('addtodo'))
    return render_template("login.html")


#  ---------------------------------------   logout   ---------------------------------------



@app.route('/logout',methods=['GET', 'POST'])
def logout():
  if 'username' in session:  
    id=session['user_id']
    query='''mutation{
                    logout(id:%s)
                        {
                            msg
                        }  
                    }'''%(id)
   
    response=requests.post(url=url,json={"query":query})
    
    if response.json()['data']['logout'] is None:
        msg='You are not valid User kindly login again'
        return render_template('login.html',msg=msg)
    else:
        session.pop('username', None)                
        session.pop('user_id', None)
        session.pop('token', None)
        
        msg=response.json()['data']['logout']['msg']
        return render_template('login.html',msg=msg)
  return redirect(url_for('login'))

#  ---------------------------------------   ALL Todo  ---------------------------------------
# @app.route('/todo',methods=['GET'])
# def todoadd():
  
#         query =  '''query{
#                             allTodo{
#                                 id
#                                 task
#                                user{
#                                    username
#                                    id
#                                }
#                              }
#                         }'''
            
#         response = requests.get(url=url, json={"query":query})
#         print(response.json())
#         post =response.json()['data']['allTodo']
#         return  render_template("home.html",post=post)    



# ---------------------------------------   Todo by user id  ---------------------------------------


@app.route('/todoget/<int:id>' , methods=['GET'])
def gettodo(id):
    
    if  'username' in session :
        query =  '''  query{
                        todoGet(id:%s){
                            id
                            task
                            datetime
                            user{
                                id
                                username
                        }
                        }
                    }'''%(id)
        headers = {'Authorization': f"JWT {session['token']}"}       
        response = requests.get(url=url, json={"query":query}, headers=headers)
        post  = response.json()['data']['todoGet']
        return  render_template("home.html",post=post)    
    return redirect(url_for('login'))
    




#  ---------------------------------------   Add Todo ---------------------------------------
# @app.route('/login', methods=['GET'])
# def loginpage():
#     return render_template('login.html')


@app.route('/todo', methods=['POST','GET'])
def addtodo():
   if 'username' in session:  
    id=session['user_id']   
    if request.method == "POST":
        task  = request.form['task']
        user = request.form['user']
        print(task, user)
        query = '''mutation{
  
                 toodadd(task:"%s",user:%s){
                                                                                               
                todoadd{
                
                task 
                 user {
                    id 
                     }
                      }
                   }
                   }''' %(task,id)
          
        headers = {'Authorization': f"JWT {session['token']}"}
        response = requests.post(url=url, json={"query":query},headers=headers)
        
        print(response.json(),"dsdsdsdsdjsldkjslkdjsljdjsdljsldjs")
        return redirect(url_for('addtodo'))

    return render_template('todoadd.html')
   return redirect(url_for('login'))  


#  ---------------------------------------   update Todo ---------------------------------------

@app.route('/todoupdate/<int:id>', methods=['POST','GET'])
def updatetodo(id):
 if  'username' in session : 
    data= ''' query{
  
        todoById(id:%s){
           
            task
           
            
        }
        }'''%(id)
        
    print(data,"ds,ndsdsdjsddnsndsd-------------------------s")    
    data_res=requests.get(url=url,json={"query":data})
    data=data_res.json()['data']['todoById']        
    print(data,"sa,slass====================")
    
    
    if request.method == "POST":
        task = request.form['task']
        
        
        
        query = '''
        
            mutation{
                
                    todoupdate(task:"%s",idPost:%s){
                        
                    todosUpdate{
                     
                        task

                    }
                }
            }

                 ''' %(task,id)
        headers = {'Authorization': f"JWT {session['token']}"}
        response = requests.post(url=url, json={'query':query}, headers=headers)     

        print(response.json()["data"],"dsmdsdsdksdmsdmlksmdlms,dmsmdklmskdms=================")

        return redirect(url_for('addtodo'))

    return render_template('todo_update.html',data=data)
 return redirect(url_for('login'))

#  ----------------------------------------  todo delete ----------------------------------



@app.route('/tododelete/<int:id>', methods=['GET',"POST"])
def tododelete(id):
  if  'username' in session :  
    data = '''
        mutation{
  
            tododelete(id:%s){
                
                  msg
                
            }
            }''' %(id)
    headers = {'Authorization': f"JWT {session['token']}"}
    response = requests.post(url=url , json={"query":data}, headers=headers)
    print(response)
    return redirect(url_for('tododelete'))
  return redirect(url_for('login'))


 
app.run(debug=True)


