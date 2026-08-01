from datetime import datetime

def generar_tirilla(arqueo, ventas, acpm, gastos, inventario):
    line = "-" * 42
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    txt = []
    txt.append(" MOTEL DONDE MAMÁ - CIERRE DE TURNO ")
    txt.append(line)
    txt.append(f"Fecha: {fecha}")
    txt.append(line)

    # VENTAS
    txt.append("VENTAS DEL DÍA")
    total_ventas = 0
    for v in ventas:
        hab = v.get("numhabitacion", "")
        total = v.get("total", 0)
        txt.append(f"HAB {hab:<3}  TOTAL: ${total}")
        total_ventas += total
    txt.append(f"TOTAL VENTAS: ${total_ventas}")
    txt.append(line)

    # ACPM
    txt.append("GASTO ACPM")
    total_acpm = 0
    for a in acpm:
        txt.append(f"{a['fecha']}  {a['litros']}L  ${a['valor_total']}")
        total_acpm += a["valor_total"]
    txt.append(f"TOTAL ACPM: ${total_acpm}")
    txt.append(line)

    # GASTOS VARIOS
    txt.append("GASTOS VARIOS")
    total_gastos = 0
    for g in gastos:
        txt.append(f"{g['desc']}  ${g['valor']}")
        total_gastos += g["valor"]
    txt.append(f"TOTAL GASTOS: ${total_gastos}")
    txt.append(line)

    # INVENTARIO
    txt.append("INVENTARIO – CONSUMOS")
    for item in inventario:
        txt.append(f"{item['nombre']}  -{item['cant']} {item['unidad']}")

    txt.append(line)
    txt.append(f"NETO DEL DÍA: ${total_ventas - total_acpm - total_gastos}")
    txt.append(line)
    txt.append("        FIN DEL REPORTE")
    txt.append(line)

    return "\n".join(txt)
