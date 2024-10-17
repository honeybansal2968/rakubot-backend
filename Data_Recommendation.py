import Gemini_API
import pandas as pd
from  flask import jsonify
import ast
from dotenv import load_dotenv
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
# print("cuda",os.environ["CUDA_VISIBLE_DEVICES"])
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# Load a pre-trained model (e.g., Sentence-BERT)
sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # A fast model for embeddings
# Load the environment variables from the .env file
load_dotenv()
pinecone_api_key = os.getenv('PINECONE_API_KEY')
# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
pinecone_index = pc.Index("product-index")
data = pd.DataFrame(pd.read_csv('https://drive.google.com/uc?id=1Ep1NHgOS8030aUJGieWL4_T3Gd8MOgES'))

def getRecommendedProducts(query):
    query_vector = sentence_model.encode(query).tolist()
    result = pinecone_index.query(vector=query_vector, top_k=100)
    dic={}
    scores_list= []
    if result['matches'] == []:
        return {"data":{"1":data.iloc[0]},"scores":[]}
    for match in result['matches']:
        row=data[data["product_id"]==int(match['id'])]
        try:
            dic[match['id']]={
                "id":str(row.product_id.iloc[0]),
                "name":str(row.name.iloc[0]),
                "size":str(row.size),
                "description":ast.literal_eval(row.description.iloc[0]),
                "images": ast.literal_eval(row.images.iloc[0]),
                "sku":str(row.sku.iloc[0]),
                "price":str(row.price.iloc[0]),
                }
            scores_list.append(match['score'])
        except Exception as e:
            print("error ",e)
            continue
    first_10_entries = []
    product_data = [(key, value) for key, value in data.items()]
    if (len(product_data)>10):
        first_10_entries = dict(product_data[:10])
    else:
        first_10_entries = dict(product_data)
    message = getGeminiResponse(query,first_10_entries, scores_list[0])
    return {
        "data":dic,
        "scores":scores_list,
        "message":message
    }

def getGeminiResponse(query,data,score):
    
    message=Gemini_API.getLLMResponse(query,data,score)
    return message
def show_recommendation(Prompt):
    list=Gemini_API.give_indices(Prompt)
    print("Hello")
    list.append('1')
    # print(list)
    final_li=[]
    for i in list:
        try:
            final_li.append(int(i))
        except Exception as e:
            print(e)
            continue

    dic={}
    for i in final_li:
        row = data.iloc[i]
        try:
            dic[i]={
                "id":str(row.id),
                "name":str(row["name"]),
                "size":str(row.size),
                "description":ast.literal_eval(row.description),
                "images": ast.literal_eval(row.images),
                "sku":str(row.sku),
                "price":str(row.price)
                }
        except:
            continue
        # print("imageslist",ast.literal_eval(row.images))
       
    print(dic)
    return jsonify(dic)

def show_image_recommendation(path):
    prompt=Gemini_API.images(path)
    return getRecommendedProducts(prompt)

def get_data(default_data):
    final_li =default_data
    dic = {}
    for i in final_li:
        row = data.iloc[i]
        try:
            dic[i] = {
                "id": str(row.product_id),
                "name": str(row["name"]),
                "size": str(row.size),
                "description": ast.literal_eval(row.description),
                "images": ast.literal_eval(row.images),
                "sku": str(row.sku),
                "price": str(row.price)
            }
        except:
            continue
    return dic