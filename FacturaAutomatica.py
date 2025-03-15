import os
import subprocess
import requests
import logging
import json
import base64
from fpdf import FPDF
import xml.etree.ElementTree as ET

#  Variables para el certificado
CERT_FILE = "certificate.pem"   # Reemplázarlo cuando tengamos el oficial
KEY_FILE = "privateKey.pem"     # Reemplázarlo cuando tengamos el oficial

#  Variable para activar/desactivar el envío a la DIAN
ENVIAR_A_DIAN = False  # 🔹 Cambiar a True cuando tengamos credenciales oficiales

#  URL de la DIAN
URL_DIAN = "https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc"

#  Token y credenciales (Reemplazar cuando estén disponibles)
TOKEN = "TU_TOKEN_AQUI"
USUARIO_DIAN = "USUARIO_DIANAQUI"
CONTRASEÑA_DIAN = "CONTRASEÑA_DIANAQUI"

def configurar_logs():
    logging.basicConfig(filename="facturacion.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def ejecutar_index_js():
    """Ejecuta index.js para generar factura.json y factura.xml."""
    try:
        resultado = subprocess.run(["node", "index.js"], capture_output=True, text=True)
        if resultado.returncode == 0:
            logging.info(" index.js ejecutado correctamente.")
        else:
            logging.error(f" Error ejecutando index.js: {resultado.stderr}")
    except Exception as e:
        logging.error(f" Excepción al ejecutar index.js: {str(e)}")

def firmar_xml(xml_file, signature_file):
    try:
        comando = [
            "openssl", "smime", "-sign",
            "-in", xml_file,
            "-out", signature_file,
            "-signer", CERT_FILE,
            "-inkey", KEY_FILE,
            "-outform", "DER",
            "-nodetach",
            "-binary"
        ]
        
        resultado = subprocess.run(comando, capture_output=True)
        if resultado.returncode == 0:
            logging.info(" Firma generada correctamente en formato DER.")
            return True
        else:
            logging.error(f" Error al generar la firma: {resultado.stderr}")
            return False
    except Exception as e:
        logging.error(f" Excepción al firmar XML: {str(e)}")
        return False

def enviar_a_dian(xml_firmado):
    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
        "SOAPAction": "http://wcf.dian.colombia/IWcfDianCustomerServices/SendBillSync",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    with open(xml_firmado, "r", encoding="utf-8") as f:
        xml_content = f.read()
    
    soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wcf="http://wcf.dian.colombia">
        <soapenv:Header>
            <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                <wsse:UsernameToken>
                    <wsse:Username>{USUARIO_DIAN}</wsse:Username>
                    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{CONTRASEÑA_DIAN}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </soapenv:Header>
        <soapenv:Body>
            <wcf:SendBillSync>
                <wcf:fileName>factura_firmada.xml</wcf:fileName>
                <wcf:contentFile><![CDATA[{xml_content}]]></wcf:contentFile>
            </wcf:SendBillSync>
        </soapenv:Body>
    </soapenv:Envelope>"""

    try:
        response = requests.post(URL_DIAN, data=soap_request, headers=headers)
        logging.info(f" Respuesta DIAN: {response.status_code} - {response.text}")

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            ns = {"ns": "http://wcf.dian.colombia"}
            cufe = root.find(".//ns:Cufe", ns)

            if cufe is not None:
                cufe_text = cufe.text
                logging.info(f"✅ CUFE recibido: {cufe_text}")
                generar_pdf(cufe_text)
            else:
                logging.warning("⚠ No se encontró CUFE en la respuesta de la DIAN.")

            return response.text
        else:
            logging.error(f" Error en la respuesta de la DIAN: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f" Excepción al enviar a la DIAN: {str(e)}")
        return None

def generar_pdf(cufe="CUFE_DE_PRUEBA"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Factura Electrónica", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"CUFE: {cufe}", ln=True, align='C')
    pdf.output("factura.pdf")
    logging.info(" PDF generado con éxito: factura.pdf")

def main():
    configurar_logs()
    ejecutar_index_js()
    
    xml_file = "factura.xml"
    signature_file = "firma.p7s"
    
    if not os.path.exists(xml_file):
        logging.error(" No se generó factura.xml, proceso detenido.")
        return
    
    if firmar_xml(xml_file, signature_file):
        logging.info(" Firma generada correctamente. Insertándola en el XML...")
        
        if ENVIAR_A_DIAN:
            logging.info(" Envío a la DIAN activado.")
            enviar_a_dian("factura_firmada.xml")
        else:
            logging.info(" Modo pruebas: No se envió a la DIAN.")
            generar_pdf()
    else:
        logging.error(" No se pudo firmar el XML, proceso detenido.")

if __name__ == "__main__":
    main()