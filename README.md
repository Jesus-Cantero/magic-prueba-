# MTG Wiki

Web app en Flask para consultar cartas de Magic the Gathering y crear tus propios mazos.
Los datos de las cartas vienen de la API de Scryfall (https://scryfall.com/docs/api).

## Cómo ponerlo en marcha (en VS Code)

1. Abre esta carpeta en VS Code (`Archivo > Abrir carpeta...`).
2. Abre una terminal integrada (`Terminal > Nueva terminal`) y crea un entorno virtual:

   ```
   python -m venv venv
   ```

   Actívalo:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Descarga las cartas de Scryfall a tu base de datos local (tarda uno o dos minutos, son unas 30.000 cartas):

   ```
   python download_cards.py
   ```

   Esto crea el archivo `mtg_cards.db`. Solo hace falta ejecutarlo una vez (o de vez en cuando, si quieres actualizar los datos con las últimas ediciones).

5. Arranca el servidor:

   ```
   python app.py
   ```

6. Abre tu navegador en **http://127.0.0.1:5000**

## Qué puedes hacer

- Buscar cartas por nombre, texto, tipo o color.
- Ver la ficha completa de cada carta (imagen, coste, texto, legalidades...).
- Crear mazos con nombre y formato.
- Añadir cartas a un mazo desde su ficha, y quitarlas desde la vista del mazo.

## Ideas para ampliarlo más adelante

- Filtro por coste de maná (cmc) y por legalidad en un formato concreto.
- Exportar un mazo a texto plano (formato que aceptan MTGO/Arena).
- Contador de curva de maná del mazo con un gráfico.
- Login de usuario si quieres tener varios "perfiles" de mazos.
- Búsqueda avanzada tipo Scryfall (operadores como `cmc>3`).
