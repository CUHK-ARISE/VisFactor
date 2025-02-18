
import base64
import requests
import json

api_key = "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"

def encode_image(image_path):
	with open(image_path, "rb") as image_file:
		return base64.b64encode(image_file.read()).decode('utf-8')

f = open('/Users/zhangmingyue/Desktop/FCRT')

data = json.load(f)

option = input("Select option(0 for split, 1 for group): ")

score = 0

if option == 1:

for i in range (0, 15):
	question_image_path = data['Questions'][i]['QuestionImagePath']
	image_path = data['Questions'][i]['ImagePath'][0]

	# Getting the base64 string
	base64_question_image = encode_image(question_image_path)
	base64_image = encode_image(image_path)

	headers = {
	  "Content-Type": "application/json",
	  "Authorization": f"Bearer {api_key}"
	}

	payload = {
	  "model": "gpt-4-vision-preview",
	  "messages": [
		{
		  "role": "user",
		  "content": [
			{
			  "type": "image_url",
			  "image_url": {
				"url": f"data:image/jpeg;base64,{base64_question_image}"
			  }
			},
			{
			  "type": "image_url",
			  "image_url": {
				"url": f"data:image/jpeg;base64,{base64_image}"
			  }
			},
			{
			  "type": "text",
			  "text": data['Instruction']
			}
		  ]
		}
	  ],
	  "max_tokens": 300
	}

	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

	print(response.json()['choices'][0]['message']['content'])

	if data['Questions'][i]["Answer"][0] in response.json()['choices'][0]['message']['content']:
		print("correct!")
		score += 1
	else:
		print("incorrect!")

print(score)

