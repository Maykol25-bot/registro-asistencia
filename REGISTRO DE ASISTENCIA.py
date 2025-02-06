from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Configurar Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurar acceso a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
cred_path = r"C:\Users\VENUS.SUCAPUCA\Desktop\Pythom\Registro de asistencia\liquid-agility-450012-u8-570c585e86ec.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)

# Abrir hojas de cálculo
sheet_users = client.open("BASE DE DATOS DE USUARIOS").worksheet("Usuarios")
sheet_meeting = client.open("DATOS DE REUNION").worksheet("Reunion")
sheet_attendance = client.open("REGISTRO DE ASISTENCIA").worksheet("Asistencia")

# Obtener datos de la reunión
meeting_data = sheet_meeting.get_all_records()
current_meeting = next((row for row in meeting_data if row["Habilitar"] == "habilitado"), None)

if current_meeting:
    tema_actual = current_meeting["TEMA"]
    expositor_actual = current_meeting["EXPOSITOR"]
    lugar_actual = current_meeting["LUGAR"]
else:
    tema_actual, expositor_actual, lugar_actual = "Registro de asistencia deshabilitado", "", ""

# Rutas de Flask

@app.route('/')
def index():
    return render_template('index.html', tema=tema_actual, expositor=expositor_actual, lugar=lugar_actual, fecha=datetime.date.today())

@app.route('/buscar', methods=['POST'])
def buscar_dni():
    dni = request.form['dni']
    if not dni:
        flash("Ingrese un DNI válido")
        return redirect(url_for('index'))

    users_data = sheet_users.get_all_records()
    user = next((row for row in users_data if str(row["DNI"]) == dni), None)

    if user:
        return render_template('index.html', tema=tema_actual, expositor=expositor_actual, lugar=lugar_actual, fecha=datetime.date.today(),
                               nombre=user['Nombre'], cargo=user['Cargo'], dni=dni)
    else:
        flash("DNI no encontrado")
        return redirect(url_for('index'))

@app.route('/registrar', methods=['POST'])
def registrar_asistencia():
    dni = request.form['dni']
    nombre = request.form['nombre']
    cargo = request.form['cargo']

    if tema_actual == "Registro de asistencia deshabilitado":
        flash("Registro de asistencia deshabilitado")
        return redirect(url_for('index'))

    if not dni or not nombre:
        flash("Debe buscar su DNI primero")
        return redirect(url_for('index'))

    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet_attendance.append_row([dni, nombre, cargo, datetime.date.today().strftime("%Y-%m-%d"), fecha_hora, tema_actual])

    flash("GRACIAS POR REGISTRAR SU ASISTENCIA")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
