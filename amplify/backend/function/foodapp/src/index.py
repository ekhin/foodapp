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
    try:
        imageResult = recognizeImage()
        if len(imageResult) > 0 :
            for i in imageResult["CustomLabels"]:
                nutrientList = []
                recognizedFood ={}
                if i["Name"] == "Food":
                    continue
                foodName = i["Name"]
                print("foodName")
                print(foodName)
                if foodName == "ice_cream":
                    foodName = "icecream"
                if foodName == "large_ice_cream":
                    foodName = "VANILLA BEAN ICECREAM"
                if foodName == "small_ice_cream":
                    foodName = "PREMIUM CHOICE ICECREAM"
                if foodName == "hot_dog":
                    foodName = "hotdog"
                if foodName == "large_hot_dog":
                    foodName = "Gourmet hotdog"
                if foodName == "small_hot_dog":
                    foodName = "Hotdog relish"
                if foodName == "club_sandwich":
                    foodName = "sandwich"
                if foodName == "large_club_sandwich":
                    foodName = "pork sandwich"
                if foodName == "small_club_sandwich":
                    foodName = "pastrami sandwich"
                if foodName == "french_fries":
                    foodName = "Potato, french fries, NFS"
                if foodName == "large_french_fries":
                    foodName = "Potato, french fries, fast food"
                if foodName == "small_french_fries":
                    foodName = "Potato, home fries, from fresh"
                if foodName == "large_hamburger":
                    foodName = "Double cheeseburger (McDonalds)"
                if foodName == "small_hamburger":
                    foodName = "Cheeseburger (McDonalds)"
                if foodName == "large_pizza":
                    foodName = "PIZZA HUT 14"
                if foodName == "small_pizza":
                    foodName = "SLICED PIZZA"
                if foodName == "pizza":
                    foodName == "Dessert pizza"
                # if('Burger' in foodName):
                #     url = "https://api.nal.usda.gov/fdc/v1/foods/search?"+ "api_key="+API_KEY+'&query="'+foodName+'" mcdonald'
                # else:
                url = "https://api.nal.usda.gov/fdc/v1/foods/search?"+ "api_key="+API_KEY+'&query="'+foodName+'"'
                # print(url)
                responseBody = http.request('GET', url)
                response = json.loads(responseBody.data)
                print(response)
                food = response['foods'][0]
                recognizedFood['description'] = food['description']

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

