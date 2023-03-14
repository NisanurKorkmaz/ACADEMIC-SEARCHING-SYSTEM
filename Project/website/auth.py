
from re import search
from flask import Blueprint, redirect, render_template, request, flash, url_for, jsonify
from neo4j import GraphDatabase
from numpy import result_type

auth = Blueprint('auth', __name__)

DBConnection=GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "1234"))
session=DBConnection.session()


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get('inputUsername')
        password = request.form.get('inputPassword')
        if username=="admin":
            if password=="1234":
                return redirect(url_for("auth.admin"))
        elif username == "gulay" :
            if password=="1234":
                return redirect(url_for("auth.user"))
        elif username=="nisa" and password=="0000": 
            return redirect(url_for("auth.user"))

    return render_template("login.html", boolean=True)

@auth.route('/logout')
def logout():
    return render_template("main.html")

@auth.route('/admin', methods=['GET','POST'])
def admin():

    if request.method == "POST":
        #database'de mevcut arastirmacilarin isimlerini listeliyor
        arastirmaci_listesi=[]
        d="MATCH (n:ARASTIRMACI) return distinct n.name"
        result=session.run(d)
        for dd in result:
            arastirmaci_listesi.append(dd[0])

        arastirmaci_id = request.form.get('arastirmaci_id')
        arastirmaci_adi = request.form.get('arastirmaci_adi')
        arastirmaci_soyadi = request.form.get('arastirmaci_soyadi')
        yayin_adi = request.form.get('yayin_adi')
        yayin_yili = request.form.get('yayin_yili')
        yayin_yeri = request.form.get('yayin_yeri')
        yayin_turu = request.form.get('yayin_turu')

        if arastirmaci_adi in arastirmaci_listesi:
            yayin_id=23
            yayin_isimSoyisim=arastirmaci_adi+" "+arastirmaci_soyadi
            yayinEkleme="CREATE (Y:YAYINLAR{yayinID: $yayin_id, yayinAdi:$yayin_adi, yayinYili:$yayin_yili, yayinYeri:$yayin_yeri, yayinTuru:$yayin_turu, yazarlar:$yayin_isimSoyisim})"
            session.run(yayinEkleme, yayin_id=yayin_id,yayin_adi=yayin_adi, yayin_yili=yayin_yili, yayin_turu=yayin_turu,yayin_yeri=yayin_yeri, yayin_isimSoyisim=yayin_isimSoyisim)
            
            baglanti="MATCH (a:ARASTIRMACI), (b:YAYINLAR) WHERE a.name=$kisi AND b.yayinAdi=$yayinAdi CREATE (a)-[:YAYIN_YAZARI]->(b)"
            session.run(baglanti, kisi=arastirmaci_adi, yayinAdi=yayin_adi)
            flash("Publication added successfully", category="success")
        else :
            #kisi ekleme 
            queryy="CREATE (N:ARASTIRMACI{id:$arastirmaci_id, name:$arastirmaci_adi, surname:$arastirmaci_soyadi, yayinAdi:$yayin_adi, yayinYili:$yayin_yili, yayinYeri:$yayin_yeri, yayinTuru:$yayin_turu})"
            session.run(queryy, arastirmaci_id=arastirmaci_id, arastirmaci_adi=arastirmaci_adi, arastirmaci_soyadi=arastirmaci_soyadi, yayin_adi=yayin_adi, yayin_yili=yayin_yili, yayin_yeri=yayin_yeri, yayin_turu=yayin_turu)
            
            #publication ekleme
            yayin_id=28
            yayin_isimSoyisim=arastirmaci_adi+" "+arastirmaci_soyadi
            yayinEklemee="CREATE (Y:YAYINLAR{yayinID: $yayin_id, yayinAdi:$yayin_adi, yayinYili:$yayin_yili, yayinYeri:$yayin_yeri, yayinTuru:$yayin_turu, yazarlar:$yayin_isimSoyisim})"
            session.run(yayinEklemee, yayin_id=yayin_id,yayin_adi=yayin_adi, yayin_yili=yayin_yili, yayin_turu=yayin_turu,yayin_yeri=yayin_yeri, yayin_isimSoyisim=yayin_isimSoyisim)
            
            #baglanti 
            baglantii="MATCH (a:ARASTIRMACI), (b:YAYINLAR) WHERE a.name=$kisi AND b.yayinAdi=$yayinAdi CREATE (a)-[:YAYIN_YAZARI]->(b)"
            session.run(baglantii, kisi=arastirmaci_adi, yayinAdi=yayin_adi)

            flash("User registered successfully", category="success")
            return render_template("admin.html")
    return render_template("admin.html")

@auth.route('/user')
def user():
    return render_template("user.html")

@auth.route("/ajaxlivesearch",methods=["POST","GET"])
def ajaxlivesearch():
    if request.method == 'POST':
        search_word = request.form['query']
        liste =[]
        if search_word ==' ':
            
            query1="MATCH (n:ARASTIRMACI)-[:YAYIN_YAZARI]->(m:YAYINLAR) return distinct n.name, n.surname, n.id, m.yayinAdi, m.yayinYili, m.yayinYeri"
            a=session.run(query1) 
            
            for a1 in a :
                employee={
                "id" : "",
                "name" : "",
	            "surname" : "",
                "yayinAdi" : "",
                "yayinYili" : "",
                "yayinYeri" : ""
            }
                employee.update({"name" : a1[0]})
                employee.update({"surname" : a1[1]})
                employee.update({"id" : a1[2] })
                employee.update({"yayinAdi" : a1[3]})
                employee.update({"yayinYili" : a1[4]})
                employee.update({"yayinYeri" : a1[5]})
                liste.append(employee)
        
        else :
            search_word=search_word.capitalize()
            #query2="MATCH (n) where n.name='{}' return n.name, n.surname, n.id, n.yayinAdi, n.yayinYili, n.yayinYeri  ".format(search_word)
            query2="MATCH (n:ARASTIRMACI)-[:YAYIN_YAZARI]->(m:YAYINLAR) WHERE n.name='{}' or n.surname='{}' or m.yayinAdi='{}' or m.yayinYili='{}' return distinct  n.name, n.surname, n.id, m.yayinAdi, m.yayinYili, m.yayinYeri".format(search_word, search_word, search_word, search_word)
            a=session.run(query2) 
            
            for a1 in a :
                employee={
                "id" : "",
                "name" : "",
	            "surname" : "",
                "yayinAdi" : "",
                "yayinYili" : "",
                "yayinYeri" : ""
            }
                employee.update({"name" : a1[0]})
                employee.update({"surname" : a1[1]})
                employee.update({"id" : a1[2] })
                employee.update({"yayinAdi" : a1[3]})
                employee.update({"yayinYili" : a1[4]})
                employee.update({"yayinYeri" : a1[5]})
                liste.append(employee)
                
            
        
        return jsonify({'htmlresponse': render_template ('table.html', employee=liste )})


@auth.route('/graph/<istek>')
def graph(istek):
    
    i="MATCH (n:ARASTIRMACI) WHERE n.name='{}' return distinct n.name, n.surname".format(istek)
    isimsoyisim=session.run(i, istek=istek)
    #s ustune tiklanan kisinin isim ve soyisimi
    s = ""
    for i in isimsoyisim:
        s=s+i[0]+" "+i[1]
    
    #yayinlar o kisinin yayinlarinin listesi 
    y="MATCH (n:ARASTIRMACI)-[:YAYIN_YAZARI]->(m:YAYINLAR) WHERE n.name='{}' return distinct m.yayinAdi".format(istek)
    yayinisimleri=session.run(y, istek=istek)
    
    yayinlar=[]
    for yy in yayinisimleri:
        yayinlar.append(yy[0])
    
    #kisinin ortak calisanlari oldugu liste 
    o="MATCH (a:ARASTIRMACI)-[:ORTAK_CALISIR]->(b:ARASTIRMACI) WHERE a.name='{}' return distinct b.name, b.surname".format(istek)
    ortak_calisan=session.run(o, istek=istek)
    ortak_calisan_listesi=[]
    temp=""
    for i in ortak_calisan:
        temp=i[0]+" "+i[1]
        ortak_calisan_listesi.append(temp)
    #print(ortak_calisan_listesi)
    return render_template("graph.html", istek=s, ortaklar=ortak_calisan_listesi, yayinlar=yayinlar)


