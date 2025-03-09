import os
import subprocess
import requests
import logging
import xml.etree.ElementTree as ET
import json

def configurar_logs():
    logging.basicConfig(filename="facturacion.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generar_xml_desde_json(json_data, xml_output):
    try:
        factura = ET.Element("Invoice")
        ET.SubElement(factura, "ID").text = json_data["Invoice"]["ID"]
        ET.SubElement(factura, "IssueDate").text = json_data["Invoice"]["IssueDate"]
        ET.SubElement(factura, "InvoiceTypeCode").text = json_data["Invoice"]["InvoiceTypeCode"]
        
        supplier = ET.SubElement(factura, "AccountingSupplierParty")
        party_supplier = ET.SubElement(supplier, "Party")
        ET.SubElement(party_supplier, "Name").text = json_data["Invoice"]["AccountingSupplierParty"]["Party"]["Name"]
        ET.SubElement(party_supplier, "CompanyID").text = json_data["Invoice"]["AccountingSupplierParty"]["Party"]["CompanyID"]
        
        customer = ET.SubElement(factura, "AccountingCustomerParty")
        party_customer = ET.SubElement(customer, "Party")
        ET.SubElement(party_customer, "Name").text = json_data["Invoice"]["AccountingCustomerParty"]["Party"]["Name"]
        ET.SubElement(party_customer, "CompanyID").text = json_data["Invoice"]["AccountingCustomerParty"]["Party"]["CompanyID"]
        
        total = ET.SubElement(factura, "LegalMonetaryTotal")
        ET.SubElement(total, "PayableAmount").text = str(json_data["Invoice"]["LegalMonetaryTotal"]["PayableAmount"])
        
        invoice_lines = ET.SubElement(factura, "InvoiceLine")
        for item in json_data["Invoice"]["InvoiceLine"]:
            line = ET.SubElement(invoice_lines, "Line")
            ET.SubElement(line, "ID").text = item["ID"]
            item_element = ET.SubElement(line, "Item")
            ET.SubElement(item_element, "Name").text = item["Item"]["Name"]
            price = ET.SubElement(line, "Price")
            ET.SubElement(price, "PriceAmount").text = str(item["Price"]["PriceAmount"])
            ET.SubElement(line, "InvoicedQuantity").text = str(item["InvoicedQuantity"])
        
        tree = ET.ElementTree(factura)
        tree.write(xml_output)
        logging.info("XML generado correctamente.")
        return True
    except Exception as e:
        logging.error(f"Error al generar XML: {str(e)}")
        return False

def firmar_xml(xml_file, cert_file, key_file, output_file):
    try:
        comando = [
            "openssl", "smime", "-sign",
            "-in", xml_file,
            "-out", output_file,
            "-signer", cert_file,
            "-inkey", key_file,
            "-outform", "PEM",  # Cambiar a "PEM"
            "-nodetach"
        ]
        
        resultado = subprocess.run(comando, capture_output=True, text=True)
        if resultado.returncode == 0:
            logging.info("XML firmado correctamente.")
            return True
        else:
            logging.error(f"Error al firmar el XML: {resultado.stderr}")
            return False
    except Exception as e:
        logging.error(f"Excepción al firmar XML: {str(e)}")
        return False

def enviar_a_dian(xml_firmado):
    url_dian = "https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc"  # Endpoint de pruebas
    headers = {"Content-Type": "application/xml"}
    
    try:
        with open(xml_firmado, "rb") as file:
            response = requests.post(url_dian, data=file, headers=headers)
            
        if response.status_code == 200:
            logging.info("Factura enviada correctamente a la DIAN.")
            return response.text
        else:
            logging.error(f"Error en la respuesta de la DIAN: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Excepción al enviar a la DIAN: {str(e)}")
        return None

def main():
    configurar_logs()
    
    json_factura = {
        "Invoice": {
            "ID": "1001",
            "IssueDate": "2025-03-08",
            "InvoiceTypeCode": "01",
            "AccountingSupplierParty": {
                "Party": {
                    "Name": "Distribuidora XYZ",
                    "CompanyID": "900123456-7"
                }
            },
            "AccountingCustomerParty": {
                "Party": {
                    "Name": "Cliente ABC",
                    "CompanyID": "123456789-0"
                }
            },
            "LegalMonetaryTotal": {
                "PayableAmount": 50000
            },
            "InvoiceLine": [
                {"ID": "1", "Item": {"Name": "Producto A"}, "Price": {"PriceAmount": 25000}, "InvoicedQuantity": 2}
            ]
        }
    }
    
    xml_file = "factura.xml"
    cert_file = "certificate.pem"
    key_file = "privateKey.pem"
    output_file = "factura_firmada.xml"
    
    if generar_xml_desde_json(json_factura, xml_file):
        if firmar_xml(xml_file, cert_file, key_file, output_file):
            logging.info("Intentando enviar factura firmada a la DIAN...")
            respuesta_dian = enviar_a_dian(output_file)
            
            if respuesta_dian:
                logging.info("Respuesta de la DIAN: " + respuesta_dian)
            else:
                logging.error("No se obtuvo respuesta válida de la DIAN.")
        else:
            logging.error("No se pudo firmar el XML, proceso detenido.")
    else:
        logging.error("No se pudo generar el XML, proceso detenido.")

if __name__ == "__main__":
    main()
