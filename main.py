#from flask import Flask, render_template, request, jsonify
import requests
import json

#爬取网站所需的东西
webInfo = {
    "tokenURL":"http://172.18.100.216/api/blade-auth/ext/api/api/oauth/token",

    "apiUrl":"http://172.18.100.216/api/datacenter/dataapiCfg/dc/getDataByConfigApi",

    "headers":{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36',
        'Connection': 'keep-alive',
        'Authorization': 'Basic c2FiZXI6c2FiZXJfc2VjcmV0',
        'Content-Type': 'application/json;charset=UTF-8',
        'Blade-Auth': ''
    },

    "requestPayload":{
        'tenantId': '999999',
        'clientId': '65ABFC56CA9C7FAFDF7A2E599F6C392B',
        'clientSecret': '942846F01B9657F257D1843FD303706A',
        'grantType': 'api'
    },


    "apiData":{
        'cfgName':'数字航道设备信息整治建筑信息数据to武汉局'
    }

}

class REdata:
    REdata_webInfo = {}
    #REdata_rep = {}


    def __init__(self,webinfo):
        self.REdata_webInfo = webinfo

    def rep(self):
        rep_token = requests.post(self.REdata_webInfo["tokenURL"],
                                  headers=self.REdata_webInfo["headers"],
                                  json=self.REdata_webInfo["requestPayload"])
        # @test
        print(rep_token.text)
        result = json.loads(rep_token.text)
        access_token = result['data']['access_token']
        # @test
        #print(access_token)
        self.REdata_webInfo["headers['Blade-Auth']"]  = access_token
        # @test
        print(self.REdata_webInfo["headers['Blade-Auth']"])

        reps_result = requests.post(self.REdata_webInfo["apiUrl"],
                                    headers=self.REdata_webInfo["headers"],
                                    json=self.REdata_webInfo["apiData"])
        reps = reps_result.json()
        # @test
        # print(type(rep))
        webInfo["headers['Blade-Auth']"] = ''
        return reps

redata = REdata(webInfo)

rep1 = redata.rep()

print(rep1)
