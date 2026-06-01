import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import os

MODEL_PATH = "ml_model/modelo_entrenado.pkl"

def entrenar_modelo(datos_historicos: list):
    """
    Recibe datos de la BD y entrena el modelo de predicción.
    """
    df = pd.DataFrame(datos_historicos)
    
    # Variables independientes (X) y dependiente (y)
    X = df[['temperatura_promedio', 'precipitacion_mm', 'costo_transporte']]
    y = df['precio_venta_tonelada']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    # Guardar modelo
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(modelo, f)
        
    return modelo.score(X_test, y_test) # Retorna el R^2 score

def predecir_precio(temperatura, precipitacion, transporte):
    """
    Realiza una predicción con los factores externos.
    """
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                modelo = pickle.load(f)
            datos_entrada = pd.DataFrame({
                'temperatura_promedio': [temperatura],
                'precipitacion_mm': [precipitacion],
                'costo_transporte': [transporte]
            })
            prediccion = modelo.predict(datos_entrada)
            return round(prediccion[0], 2)
    except Exception:
        pass

    # Fallback si no hay modelo o falla al cargar
    precio_base = 1500 + (transporte * 1.2) - (precipitacion * 0.5)
    return round(precio_base, 2)

def estimar_produccion(id_cultivo, area_hectareas):
    """
    Estima la producción en toneladas basada en el área y el tipo de cultivo.
    En un sistema real, esto usaría un modelo entrenado con suelos y clima.
    """
    # Rendimientos promedio por hectárea en el Valle Jequetepeque (ficticios para el sistema)
    rendimientos = {
        1: 9.5,  # Arroz (Ton/Ha)
        2: 12.0, # Maíz
        3: 25.0, # Cebolla
        4: 5.5,  # Espárrago
    }

    # Si el ID no está, usamos un promedio general de 8.0
    rendimiento_base = rendimientos.get(id_cultivo, 8.0)

    produccion_total = area_hectareas * rendimiento_base
    return round(produccion_total, 2)

def predecir_riesgo_plaga(id_cultivo, temperatura, precipitacion):
    """
    Calcula la probabilidad de plagas específica por cultivo.
    """
    # Riesgos base por cultivo (Sensibilidad)
    riesgos_base = {
        1: 20.0, # Arroz: Sensible a humedad (Hongo)
        2: 15.0, # Maíz: Sensible a calor (Cogollero)
        3: 25.0, # Cebolla: Muy sensible a humedad
        4: 10.0, # Espárrago: Más resistente
    }

    probabilidad = riesgos_base.get(id_cultivo, 15.0)

    # Factores climáticos
    if temperatura > 26 and precipitacion > 15:
        probabilidad += 50.0 
    elif temperatura > 22 and precipitacion > 5:
        probabilidad += 20.0

    return min(round(probabilidad, 1), 100.0)

def calcular_recomendacion_cultivos(cultivos_lista: list, meses_futuro: int = 3, trans_base: float = 150.0):
    """
    Analiza la rentabilidad proyectada para un horizonte de tiempo específico.
    Incluye modelos de costos más realistas para evitar optimismo excesivo.
    """
    from datetime import datetime

    recomendaciones = []
    mes_actual = datetime.now().month
    mes_objetivo = (mes_actual + meses_futuro - 1) % 12 + 1

    # Costos realistas por Ha (Mano de obra, insumos, preparación)
    costos_produccion = {
        1: 6500.0, # Arroz
        2: 5800.0, # Maíz
        3: 7500.0, # Cebolla
        4: 9000.0, # Espárrago
    }

    # Rendimientos promedio realistas
    rendimientos = {1: 9.0, 2: 10.0, 3: 22.0, 4: 5.0}

    for c in cultivos_lista:
        # Predecir clima para el mes objetivo
        if mes_objetivo in [1, 2, 3]: t, p = 28.5, 25.0
        elif mes_objetivo in [4, 5, 6]: t, p = 24.0, 5.0
        elif mes_objetivo in [7, 8, 9]: t, p = 20.0, 1.0
        else: t, p = 23.0, 2.0

        precio_proyectado = predecir_precio(t, p, trans_base)

        # Cálculo de ROI Realista
        costo_fijo = costos_produccion.get(c.id_cultivo, 6000.0)
        rend = rendimientos.get(c.id_cultivo, 8.0)

        ingreso_bruto = rend * precio_proyectado
        costo_total = costo_fijo + (rend * trans_base)
        ganancia = ingreso_bruto - costo_total
        roi = (ganancia / costo_total) * 100

        recomendaciones.append({
            "id_cultivo": c.id_cultivo,
            "nombre": c.nombre_cultivo,
            "viabilidad": round(roi, 1),
            "precio_est": round(precio_proyectado, 2),
            "mes_objetivo": mes_objetivo
        })

    return sorted(recomendaciones, key=lambda x: x['viabilidad'], reverse=True)