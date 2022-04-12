import requests
from pandas import DataFrame
import time
try:
	STFile=requests.get("https://estrutura.iti.gov.br/assets/structure.json", timeout=100,verify=False)
	detailsFile=requests.get("https://estrutura.iti.gov.br/assets/details.json", timeout=100,verify=False)
except Exception as e:
	print("------ Connection lost ------")
	time.sleep(5)
	raise e

print("------ Data gotten succesfully ------")

structure=STFile.json()
data=detailsFile.json()



modification_date=data["atualizado_data"]
modification_time=data["atualizado_hora"]
print("------ data for last actualisation of ",modification_date," at ",modification_time,"------")
data=data["entidades"]




def getData(temp,pid):
	item=[x for x in data if x["id"] == pid][0]
	cnpj=item["cnpj"]
	cnpj=cnpj[0:2]+'.'+cnpj[2:5]+'.'+cnpj[5:8]+'/'+cnpj[9:12]+'-'+cnpj[12:]
	temp["CNPG"]=cnpj
	try:
		temp["Telefone"]=item["telefone"]
	except Exception as e:
		temp["Telefone"]=" "
	try:
		temp["Municipio"]=item["enderecos"][0]["cidade"]
	except Exception as e:
		temp["Municipio"]=" "
	try:
		temp["UF"]=item["enderecos"][0]["uf"]
	except Exception as e:
		temp["UF"]=" "
	temp["Situacao"]="Credenciado" if item["situacao"] == 4002 else "Em Credenciamento"
	return temp
df=DataFrame()


def recGetData(item,temp,i=1):
	try:
		if item["entidade"]=="AR":
			global df
			if i==2:
				temp["AC2"]=" "
			temp["AR"]=item["nome"]
			temp=getData(temp,item["id"])
			df=df.append(temp,ignore_index=True)
			temp={"AC1":"null","AC2":"null"}
		elif "entidades_vinculadas" not in item.keys() :
			return 
		else:
			for x in item["entidades_vinculadas"]:
				aux=x["tipo"].replace('-','').upper()
				temp[aux]=x["nome"]
				recGetData(x,temp,i+1)
	except Exception as e:
		print("--------------  ",e,"  ---------------")
		print([x for x in data if x["id"] == item["id"]][0])
		raise e


# ---------------------------------- main --------------------------------------------- #
print("------ start processing Data ------")
temp={"AC1":" ","AC2":" "}
for x in structure["entidades_vinculadas"]:
	temp["AC1"]=x["nome"]
	recGetData(x,temp)
print("------ Start Saving Data ------")
resultFile="data_result1"
try:
	df.to_excel(resultFile+".xlsx")
except Exception as e:
	print("------ Probleme in saving data in file ------")
	time.sleep(5)
	raise e
	

print("------ Data saved succesfully on file",resultFile," ------")