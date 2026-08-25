import json
import os
import time
from datetime import datetime

checkpoint_path = 'C:/Users/Luis Rojas/.openclaw/workspace/checkpoint_granular.json'
final_path = 'C:/Users/Luis Rojas/.openclaw/workspace/clasificacion_granular.json'
ultimo_conocido = 0

print("Monitor GRANULAR activo - Revisando cada 5 min")
print("=" * 70)

while True:
    try:
        if os.path.exists(final_path):
            with open(final_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            n = d['metadata']['articulos_clasificados']
            print(f"\n[COMPLETADO] {n}/3575 articulos - CLASIFICACION GRANULAR FINALIZADA")
            break
        
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            n = d.get('ultimo_procesado', 0)
            if n > ultimo_conocido:
                ult = d['articulos'][-1] if d['articulos'] else {}
                pct = n / 3575 * 100
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {n}/3575 ({pct:.1f}%) - {ult.get('titulo', '')[:60]}")
                ultimo_conocido = n
    except:
        pass
    
    time.sleep(300)  # 5 minutos

