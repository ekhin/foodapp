import json
import boto3
import urllib3

http = urllib3.PoolManager()
API_KEY="e9cl5VngIZPJ3rlP0TjbPfSNatfdGzsxHreADbFR"
NUTRIENTS_NUMBER_LIST = ["203", "204", "205", "606", "269",
"306", "291", "303", "307", "301", "601", "208", "328", "618"]

def recognizeImage():
    client = boto3.client("rekognition", region_name="us-west-2")
    s3 = boto3.client("s3")
    model='arn:aws:rekognition:us-west-2:766312307144:project/test_size_recognition2/version/test_size_recognition2.2021-04-18T12.53.24/1618775602186'
    # response = client.detect_labels(Image = {"S3Object": {"Bucket": "recognize13339-dev", "Name": "public/userUpload.png"}}, MaxLabels=5, MinConfidence=70)

    # response = client.detect_labels(Image = {"S3Object": {"Bucket": "custom-labels-console-us-west-2-060fcfbb0a", "Name": "public/upload.png"}}, MaxLabels=5, MinConfidence=70)
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': "custom-labels-console-us-west-2-73aca6ff8c", 'Name': "assets/testing/upload.png"}},
         MinConfidence=20,
        ProjectVersionArn=model)
    print(response)
    return response


def nutrientHelper():
    recognizedFoodList=[]
    icecream = ["ice_cream", "large_ice_cream", "small_ice_cream"]
    hotdog = ["hot_dog", "large_hot_dog", "small_hot_dog"]
    sandwich = ["club_sandwich", "large_club_sandwich", "small_club_sandwich"]
    fries = ["french_fries", "large_french_fries", "small_french_fries"]
    burger = ["large_hamburger", "small_hamburger"]
    pizza = ["large_pizza", "small_pizza"]


    try:
        imageResult = recognizeImage()
        if len(imageResult) > 0 :
            for i in imageResult["CustomLabels"]:
                nutrientList = []
                recognizedFood ={}
                size="small"
                if i["Name"] == "Food":
                    continue
                foodName = i["Name"]
                print("foodName")
                print(foodName)
                if "large" in foodName:
                    size="large"
                if foodName in icecream:
                    foodName = "icecream"
                if foodName in hotdog:
                    foodName = "hotdog"
                if foodName in sandwich:
                    foodName = "sandwich"
                if foodName in fries:
                    foodName = "Potato, french fries, fast food"
                if foodName in burger:
                    foodName = "hamburger"
                if foodName in pizza:
                    foodName = "PIZZA HUT 14"
                # if('Burger' in foodName):
                #     url = "https://api.nal.usda.gov/fdc/v1/foods/search?"+ "api_key="+API_KEY+'&query="'+foodName+'" mcdonald'
                # else:
                url = "https://api.nal.usda.gov/fdc/v1/foods/search?"+ "api_key="+API_KEY+'&query="'+foodName+'"'
                # print(url)
                responseBody = http.request('GET', url)
                response = json.loads(responseBody.data)
                # print(response)
                if response['totalHits'] == 0:
                    break
                food = response['foods'][0]
                recognizedFood['description'] = i["Name"]

                for nutrient in food['foodNutrients']:
                    foodNutrients={}
                    if nutrient['nutrientNumber'] not in NUTRIENTS_NUMBER_LIST:
                        continue
                    elif nutrient['nutrientNumber'] == "618":
                        foodNutrients['nutrientName'] = "Trans Fat"
                    elif nutrient['nutrientNumber'] == "208":
                        foodNutrients['nutrientName'] = "Calories"
                    else:
                        foodNutrients['nutrientName'] = nutrient['nutrientName']
                    if nutrient['unitName'] == "KCAL":
                        foodNutrients['unitName'] = "CAL"
                    else:
                        foodNutrients['unitName'] = nutrient['unitName'].lower()
                    if size == "large":
                        if "burger" in i["Name"] or "fries" in i["Name"]: 
                            foodNutrients['value'] = nutrient['value'] * 2;
                        else if "pizza" in i["Name"]:
                            foodNutrients['value'] = nutrient['value'] * 10;
                        else:
                            foodNutrients['value'] = nutrient['value'] * 3;
                    else:
                        foodNutrients['value'] = nutrient['value']
                    nutrientList.append(foodNutrients)

                recognizedFood['foodNutrients'] = nutrientList
                recognizedFoodList.append(recognizedFood)
                break

        return recognizedFoodList

    except Exception as e:
        return ("error: {}", e)

def handler(event, context):
    responseObject = nutrientHelper()
    return {
        'statusCode': 200,
        'body': json.dumps(responseObject),
        'headers': {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Headers' : '*'
        }
    }
