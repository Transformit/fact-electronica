function generarFacturaJSON(numeroFactura, fecha, cliente, productos) {
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
      "InvoiceLine": productos.map((item, index) => ({
        "ID": (index + 1).toString(),
        "Item": {
          "Name": item.nombre
        },
        "Price": {
          "PriceAmount": item.precio
        },
        "InvoicedQuantity": item.cantidad
      }))
    }
  };
}

module.exports = { generarFacturaJSON };
