import json
import math
import os

def dividir_array(array, num_partes=None, tamano=None):
    if num_partes:
        paso = math.ceil(len(array) / num_partes)
    elif tamano:
        paso = tamano
        num_partes = math.ceil(len(array) / tamano)
    else:
        raise ValueError("Debe indicar num_partes o tamano.")
    return [array[i*paso:(i+1)*paso] for i in range(num_partes)]

def main():
    ruta = input("Ruta de archivo JSON (array de objetos): ").strip()
    if not os.path.exists(ruta):
        print("Archivo no encontrado.")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("El JSON debe ser un array de objetos.")
        return

    print("¿Cómo quieres dividir el archivo?")
    print("1) En X partes")
    print("2) De Y elementos cada división")
    opcion = input("Selecciona (1 o 2): ").strip()

    if opcion == "1":
        partes = int(input("¿En cuántas partes quieres dividir?: ").strip())
        subarrays = dividir_array(data, num_partes=partes)
    elif opcion == "2":
        tamano = int(input("¿De qué tamaño quieres cada parte?: ").strip())
        subarrays = dividir_array(data, tamano=tamano)
    else:
        print("Opción inválida.")
        return

    base = os.path.splitext(ruta)[0]

    for idx, sub in enumerate(subarrays, 1):
        out_file = f"{base}_parte{idx}.json"
        with open(out_file, "w", encoding="utf-8") as salida:
            json.dump(sub, salida, ensure_ascii=False, indent=2)
        print(f"Parte {idx} guardada como {out_file}")

if __name__ == "__main__":
    main()