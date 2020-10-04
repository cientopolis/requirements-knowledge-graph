from flask import Flask, render_template, request, redirect, url_for, flash,  session
from werkzeug.utils import secure_filename
from flask_session import Session
import json

#Extensiones de archivos permitidos
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.debug=True



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



 #usar  app.logger.info("asdasdasd") para imprimir en consola
# Para grabar en la cookie usar session["algo"] = datos
# Para recuperar usar    variable = session.get["algo"]
# Posiblemente tengamos que aplicar string.decode("utf-8") al string que traemos de la cookie



@app.route("/login", methods=["POST", "GET"])
def login():
    
    if(request.method == "POST"):
        if(request.form["nombre"] and request.form["email"]):
            session["nombre"] = request.form["nombre"]
            session["email"] = request.form["email"]
            return redirect("/")
    else:
        if(session.get("nombre")):
            return redirect("/")
    return render_template("login.html")



@app.route("/", methods=['POST', 'GET'])
def home():
    if(not session.get("nombre") or not session.get("email")):
        return redirect("/login")
        
    if request.method == 'POST':
        #Verifica haber recibido un archivo en POST
        if 'file'  in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            #Verifica que el archivo tenga extensión válida
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                flash('archivo subido correctamente', 'success')
                #El decode("UTF-8") es porque lo trae como ascii, por lo que las tildes y otros simbolos se ven mal
                texto_default = str(file.read().decode('UTF-8'))
                #Vuelvo a cargar la página pero con el texto leido desde el archivo
                return render_template('home.html', texto_default=texto_default)
            else:
                flash('tipo de archivo no soportado.', 'error')
        else:
            flash("no reconoce el archivo", "error")
    return render_template('home.html')



def procesar_texto_basico(_texto_basico):
    """Acá habría que invocar el código que genere el equipo 1
    por el momento solamente recibe como parametro el texto ingresado
    en la pagina de inicio y retorna una lista de strings hardcodeada"""
    return[ "Una empresa ofrece travesías en kayak.",
            "Las travesías en kayak tienen duración.",
            "La duración es un tiempo.",
            "El tiempo es medido en días.",
            "Las travesías en kayak tienen itinerario.",
            "El itinerario es un texto.",
            "La empresa ofrece travesías en kayak a kayakistas inexpertos.",
            "La empresa ofrece travesías en kayak a kayakistas expertos.",
            "Un kayakista solicita una travesía en kayak a la empresa.",
            "La travesía en kayak tiene arancel.",
            "La empresa informa el arancel a los kayakistas.",
]

@app.route("/mejorado", methods=['POST', 'GET'])
def mejorado():
    if request.method =="POST":
        if "siguiente" in request.form:
            lista_texto_mejorado = procesar_texto_basico(request.form["texto"])
            #Guardo la estructura en un diccionario creado previamente para no tener 
            #que pasarme la estructura intacta desde la vista
            session["lista_mejorado"]=json.dumps(lista_texto_mejorado)
            return render_template("mejorado.html", lista_mejorado=lista_texto_mejorado)
    #Si no se recibió el texto por POST, redirige a la página de inicio.
    return redirect("/")


@app.route("/dataframe",methods=["POST", "GET"])
def dataframe():
    if(request.method =="POST"):
        if "generar_dataframe" in request.form:
            return render_template("dataframe.html")
    return redirect("/")

def procesar_texto_mejorado(_lista_texto_mejorado):
    pass

@app.route("/grafo", methods=['POST', 'GET'])
def grafo():
    if request.method =="POST":
        if "generar_grafo" in request.form:
            #recupero del diccionario auxiliar la lista de strings
            lista_texto_mejorado = session.get("lista_mejorado")
            #muestro en consola el texto obtenido
            app.logger.info(lista_texto_mejorado)
            #procesa el texto para convertirlo a grafo
            procesar_texto_mejorado(lista_texto_mejorado)
            return render_template("grafo.html")
    #Si no se recibió el texto por POST, redirige a la página de inicio.
    return redirect("/")

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    app.run(debug=True)

