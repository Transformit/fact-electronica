function generarFacturaJSON(numeroFactura, fecha, cliente, productos) {
  // Validar datos de entrada
  if (!numeroFactura || !fecha || !cliente || !productos || !Array.isArray(productos) || productos.length === 0) {
    console.error(" Error: Datos de factura inválidos.");
    process.exit(1);
  }
  if (!cliente.nombre || !cliente.documento) {
    console.error(" Error: Datos del cliente inválidos.");
    process.exit(1);
  }
  
  return {
    "Invoice": {
      "ID": numeroFactura,
      "IssueDate": fecha,
      "InvoiceTypeCode": "01",
      "AccountingSupplierParty": {
        "Party": {
          "Name": "Distribuidora XYZ",
          "CompanyID": "900123456-7"
        }
      },
      "AccountingCustomerParty": {
        "Party": {
          "Name": cliente.nombre,
          "CompanyID": cliente.documento
        }
      },
      "LegalMonetaryTotal": {
        "PayableAmount": productos.reduce((total, item) => total + item.precio * item.cantidad, 0)
      },
      "InvoiceLine": productos.map((item, index) => {
        if (!item.nombre || typeof item.precio !== 'number' || typeof item.cantidad !== 'number') {
          console.error(" Error: Producto inválido en la factura.");
          process.exit(1);
        }
        return {
          "ID": (index + 1).toString(),
          "Item": {
            "Name": item.nombre
          },
          "Price": {
            "PriceAmount": item.precio
          },
          "InvoicedQuantity": item.cantidad
        };
      })
    }
  };
}

module.exports = { generarFacturaJSON };
