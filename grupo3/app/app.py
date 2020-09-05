from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

#Extensiones de archivos permitidos
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.debug=True



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



 #usar  app.logger.info("asdasdasd") para imprimir en consola

@app.route("/", methods=['POST', 'GET'])
def home():
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



@app.route("/mejorado", methods=['POST', 'GET'])
def mejorado():
    if request.method =="POST":
        if "siguiente" in request.form:
            #Acá es donde se debería procesar el texto que se encuentra en request.form["texto"], por ahora lo retorno asi nomas para no tener la pagina vacia
            return render_template("mejorado.html", texto=request.form["texto"])
    #Si no se recibió el texto por POST, redirige a la página de inicio.
    return redirect("/")


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)
