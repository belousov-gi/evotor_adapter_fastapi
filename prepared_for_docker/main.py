from fastapi import FastAPI, Request, Header, HTTPException, Path
from typing import Optional
from mysql.connector import connect, Error
from jose import JWTError, jwt
from config import settings


app = FastAPI()
ALGORITHM = settings['Evotor_api_key']['algoritm']

def auth_token(token_type: str, token: str):    
    if token_type == 'Bearer':
        isTokenValid = False       

        SECRET_KEY = settings['Evotor_api_key']['secret_key']               

        try:            
            decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(decoded_data)
            if decoded_data:
               isTokenValid = True            
        except JWTError as e: 
            print(e)
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")            
            

        return(isTokenValid)          
        
    else:
        raise HTTPException(status_code=403, detail="Invalid authentication scheme.")


def auth_token_users (token_type: str, token: str):

    if token_type == 'Bearer':                      

        SECRET_KEY = settings['Evotor_api_key']['secret_key']               

        try:            
            decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])           
            if decoded_data:
               user_id = decoded_data['user_id']
               return(user_id)
            else: 
               raise HTTPException(status_code=403, detail="Invalid token or expired token.")               
        except JWTError as e: 
            print(e)
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")  
        
    else:
        raise HTTPException(status_code=403, detail="Invalid authentication scheme.")



@app.post("/api/v1/user/create")
async def user_create (request: Request, authorization:  Optional[str] = Header(None)):
    try:
        split_data = authorization.split()       
        token_type = split_data[0]     
        token = split_data[1]

    except Exception as e: 
        return(e)
    
    if auth_token(token_type, token):
        
        data = await request.json()
        user_id  = data['userId']
        
        SECRET_KEY = settings['Evotor_api_key']['secret_key']
        to_encode_data = {'user_id':'\'' + user_id + '\' '}
        api_key = jwt.encode(to_encode_data, SECRET_KEY, algorithm=ALGORITHM)        

        returned_data = {
            "userId": user_id,                          
            "token": api_key
            }
        
        try:
            with connect(
                
                    host = settings['Database']['Dsn']['host'],
                    user = settings['Database']['Dsn']['username'],
                    password = settings['Database']['Dsn']['password'],
                    database = settings['Database']['Dsn']['database']

                ) as connection:           

                    create_db_query = (
                        "INSERT INTO users (user_id, api_key) VALUES (" + f" '{user_id}', '{api_key}' )"
                        )
                    
                    cursor = connection.cursor()        
                    cursor.execute(create_db_query)
                    connection.commit()
                    result = cursor.fetchall()
                    print(result)  
                    return(returned_data)                        
        
        except Error as e: 
            print (e)      

@app.post("/api/v1/user/verify")

async def user_verify (request: Request, authorization:  Optional[str] = Header(None)):
    try:
        split_data = authorization.split()       
        token_type = split_data[0]     
        token = split_data[1]

    except Exception as e: 
        return(e)
    
    if auth_token(token_type, token):
        
        data = await request.json()
        user_id  = data['userId']

        try:
            with connect(
                
                    host = settings['Database']['Dsn']['host'],
                    user = settings['Database']['Dsn']['username'],
                    password = settings['Database']['Dsn']['password'],
                    database = settings['Database']['Dsn']['database']

                ) as connection:           

                    create_db_query = (
                        "SELECT api_key FROM users WHERE user_id = " + f"'{user_id}'"
                        )
                    
                    cursor = connection.cursor()        
                    cursor.execute(create_db_query)
                    result = cursor.fetchone()
                    api_key = result[0]                  
                    
                    returned_data = {
                        "userId": user_id,                          
                        "token": api_key
                        }

                    return(returned_data)                        

        except Error as e: 
            print (e)             
        
        returned_data = {
                    "userId": user_id,                          
                    "token": token
                    }
        
        return(returned_data)

@app.put("/")
async def new_data(request: Request, authorization:  Optional[str] = Header(None)): 

    try:
        split_data = authorization.split()       
        token_type = split_data[0]     
        token = split_data[1]
    except Exception as e: return(e)     
    

    id_user = auth_token_users(token_type, token)

    if id_user:        
       

        data =  await request.json()

        print(data)  
        
        try:
            with connect(
                
                    host = settings['Database']['Dsn']['host'],
                    user = settings['Database']['Dsn']['username'],
                    password = settings['Database']['Dsn']['password'],
                    database = settings['Database']['Dsn']['database']

                ) as connection:                    

                    positions_count = (len(data['body']['positions']))
        
                    current_loop = 1
                    current_index = 0

                    while current_loop <= positions_count:

                        print('LOOP' + str(current_loop))

                        store_uuid = data['store_id']

                        product_id = data['body']['positions'][current_index]['product_id']
                        print(product_id)

                        product_name = data['body']['positions'][current_index]['product_name']
                        print(product_name)    

                        quantity = data['body']['positions'][current_index]['quantity']
                        print(quantity)

                        product_price = data['body']['positions'][current_index]['price']
                        print(product_price)

                        result_price = data['body']['positions'][current_index]['result_price']
                        print(result_price)
                        
                        payment_type = data['body']['payments'][0]['type']
                        print(payment_type)

                        receipt_date = data['body']['pos_print_results'][0]['receipt_date']
                        receipt_date = f'{receipt_date[:2]}.{receipt_date[2:4]}.{receipt_date[4:]}'
                        print(receipt_date)

                        fiscal_sign_doc_number = data['body']['pos_print_results'][0]['fiscal_sign_doc_number']                    
                        print(fiscal_sign_doc_number)

                        customer_phone = data['body']['customer_phone']
                        print(customer_phone)
                        
                        current_index = current_index + 1
                        current_loop = current_loop + 1

                        create_db_query = (" INSERT INTO sells ( \
                                            store_uuid, \
                                            product_id, \
                                            product_name, \
                                            quantity, \
                                            product_price, \
                                            result_price, \
                                            payment_type, \
                                            receipt_date, \
                                            customer_phone, \
                                            fiscal_sign_doc_number \
                                            ) VALUES (" + f" '{store_uuid}', '{product_id}', '{product_name}', {quantity}, {product_price}, {result_price}, " 
                                            f"'{payment_type}', '{receipt_date}', '{customer_phone}', '{fiscal_sign_doc_number}' )"
                        )

                        print(create_db_query)
                        cursor = connection.cursor()        
                        cursor.execute(create_db_query)
                        connection.commit()
                        cursor.fetchall()                                               
                                     

        except Error as e:

            # log_exeptions_file = open('log_exceptions_file.txt', 'a')
            # log_exeptions_file.write(e) 
            # log_exeptions_file.write('\n\n')
            # log_exeptions_file.close()

            print (e)
