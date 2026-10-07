# S.T.C — Sistema de Torneos de Cartas

Aplicación web para organizar torneos de un juego de cartas 1 contra 1 con formato de **eliminación directa**: inscripción de jugadores, mazos, rondas, emparejamientos, resultados, puntos, ranking y estadísticas.

Proyecto académico de Ingeniería de Sistemas, Universidad de Pamplona.

- **Frontend (producción):** https://sistema-torre-de-cartas.vercel.app
- **Backend (producción):** https://sistema-torre-de-cartas.onrender.com (documentación interactiva en `/docs`)

> El plan gratuito de Render duerme el servicio tras un rato sin uso: la primera petición puede tardar unos segundos.

---

## Funcionalidades

| Rol | Qué puede hacer |
|---|---|
| **Pendiente** | Se registra y espera a que un administrador le asigne un rol. |
| **Jugador** | Crea y edita sus mazos, elige mazo en cada ronda, consulta los torneos en los que participa, su historial, sus estadísticas y el ranking global. |
| **Organizador** | Crea torneos, inscribe jugadores, inicia el torneo, genera emparejamientos, registra resultados y avanza de ronda. Ve todos los torneos. |
| **Administrador** | Aprueba usuarios y asigna roles, activa o desactiva cuentas, y puede gestionar cualquier torneo. |

Además, todos los usuarios pueden editar su nombre desde **Mi cuenta**. Los nombres pueden repetirse: en torneos y rankings cada jugador se identifica con su número (`Nombre #id`).

## Reglas del sistema

- **Torneos de 4, 8, 16 o 32 jugadores.** Solo se pueden inscribir jugadores mientras el torneo está pendiente, sin duplicados ni exceso de cupos, y solo se inicia cuando está completo. Al iniciar se crea la Ronda 1.
- **Mazos:** un mazo es válido si suma **al menos 20 cartas** (contando copias) y respeta el máximo de copias de cada carta. Un jugador puede tener varios mazos.
- **Mazo por ronda:** el jugador puede cambiar de mazo hasta que el organizador genere los emparejamientos. Si no cambia, conserva el mazo con el que ganó la ronda anterior (en la primera ronda, su mazo válido más antiguo).
- **Puntos por partida (ganador):**
  - Victoria en fase normal: **3**
  - Victoria en overtime con vida del ganador mayor a 0: **2**
  - Victoria en overtime con vida del ganador en 0 o menos: **1**
  - Derrota: **0**
- El ganador debe terminar con **más vida** que el perdedor.
- **Ranking de un torneo:** ordena por la ronda en que cada jugador quedó eliminado (el campeón primero), luego por puntos del torneo y, si empatan, por vida acumulada. Los empates totales comparten posición.
- **Ranking global:** victorias, luego puntos, luego enfrentamiento directo y, por último, la fecha del último resultado (gana quien alcanzó esa marca primero).
- Las cuentas **no se borran, se desactivan**, para conservar el historial y los rankings.
- Visibilidad: un jugador solo ve los torneos en los que está inscrito; organizadores y administradores ven todos. Las cartas de un mazo solo las consulta su dueño.

> El sistema gestiona la logística del torneo. **No simula el juego:** el organizador registra manualmente el resultado de cada partida.

## Tecnologías

- **Frontend:** Angular (componentes standalone, sin Zone.js) + TypeScript + Tailwind CSS v4
- **Backend:** FastAPI (Python) + SQLAlchemy
- **Base de datos:** PostgreSQL (Supabase en la nube, o PostgreSQL local)
- **Autenticación:** JWT (`python-jose`) y contraseñas con `bcrypt` (fijado en `bcrypt==4.0.1` por compatibilidad con `passlib`)
- **Despliegue:** Render (backend) y Vercel (frontend)

## Estructura del repositorio

```
torre-de-cartas/
├── backend/
│   ├── app/
│   │   ├── main.py            # app FastAPI, CORS y routers
│   │   ├── core/              # database.py, security.py, access.py
│   │   ├── models/            # modelos SQLAlchemy
│   │   ├── schemas/           # esquemas Pydantic
│   │   └── api/v1/            # endpoints
│   ├── scripts/               # seeds y utilidades de desarrollo
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── core/              # servicios, guards e interceptor
│       ├── shared/            # layout, navbar y pipes
│       ├── models/
│       └── features/          # auth, home, tournaments, decks, ranking, stats, account, admin
├── database/
│   ├── ddl/                   # esquemas, tablas, funciones y triggers
│   └── seeds/                 # roles y catálogo de 18 cartas
├── docs/                      # requisitos y diseño del juego
├── init-local-db.ps1          # crea la base local desde cero
└── switch-env.ps1             # alterna el backend entre base local y nube
```

## Puesta en marcha en local

### Requisitos

- Python 3.x (desarrollado con 3.14) y `pip`
- Node.js y Angular CLI (`npm install -g @angular/cli`)
- Una base PostgreSQL: un proyecto de Supabase o PostgreSQL instalado en tu máquina
- Los scripts `.ps1` están pensados para **Windows PowerShell**

### 1. Base de datos

**Opción A: PostgreSQL local.** Desde la raíz del proyecto:

```powershell
.\init-local-db.ps1
```

Pide la contraseña del usuario `postgres`, crea la base `torre_de_cartas` y ejecuta, en este orden: `00_create_schemas.sql`, `01_tables.sql`, `03_functions.sql`, `02_triggers.sql` y los seeds `00_roles.sql` y `01_cards.sql`. Las rutas dentro del script son absolutas: **edítalas** para que apunten a tu carpeta.

**Opción B: Supabase.** Crea un proyecto y ejecuta los mismos archivos SQL en el mismo orden desde el SQL Editor. Para conectar desde el backend usa la cadena del **connection pooler**, no la conexión directa (esta falla por DNS en muchas redes).

### 2. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crea el archivo `backend/.env` con **solo estas dos variables**:

```
DATABASE_URL=postgresql://USUARIO:CONTRASEÑA@HOST:PUERTO/BASE
SECRET_KEY=una_clave_larga_y_aleatoria
```

Para generar la clave:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Arranca el servidor:

```powershell
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs
- Comprobar la conexión a la base: http://localhost:8000/test-db

### 3. Frontend

```powershell
cd frontend
npm install
ng serve
```

Abre http://localhost:4200. La URL del backend se configura en `src/environments` (`apiUrl`); en local debe ser `http://localhost:8000`.

### 4. Datos de demostración (solo base local)

```powershell
cd backend
python -m scripts.seed_demo
```

Crea 1 administrador, 1 organizador y 8 jugadores, cada uno con los mismos dos mazos de 20 cartas, para poder armar torneos de 4 u 8 jugadores sin preparar nada. Las credenciales de esas cuentas están definidas en el propio script. El script **se niega a ejecutarse si el `.env` apunta a una base que no sea local**.

Otros scripts útiles en `backend/scripts/`:

- `seed_dev_data.py`: crea jugadores de prueba con mazo; con `--tournament-id N` los inscribe en un torneo.

### Alternar entre base local y nube

Guarda dos archivos, `backend/.env.local` y `backend/.env.cloud` (ambos con `DATABASE_URL` y `SECRET_KEY`), y cambia entre ellos con:

```powershell
cd backend
..\switch-env.ps1 local      # o: ..\switch-env.ps1 cloud
```

Después **reinicia `uvicorn`**. Cada base tiene sus propias cuentas.

## API: resumen de endpoints

| Área | Endpoints principales |
|---|---|
| Autenticación | `POST /auth/login`, `POST /auth/register`, `GET /auth/me`, `PUT /auth/me/name` |
| Administración | `GET /auth/pending-users`, `GET /auth/users`, `PUT /auth/users/{id}/role`, `PUT /auth/users/{id}/active` |
| Torneos | `GET/POST /tournaments/`, `POST /tournaments/{id}/start`, `POST /tournaments/{id}/next-round`, `GET /tournaments/{id}/rounds`, `GET /tournaments/{id}/players`, `GET/POST /tournaments/{id}/registrations`, `GET /tournaments/{id}/ranking` |
| Jugadores | `GET /players/`, `GET/POST /players/me`, `GET /players/me/history` |
| Mazos | `GET /decks/me`, `POST /decks/`, `GET /decks/{id}`, `GET/POST /decks/{id}/cards`, `PUT/DELETE /decks/{id}/cards/{card_id}` |
| Mazo por ronda | `GET/POST /rounds/{id}/deck-selection` |
| Partidas | `GET/POST /matches/`, `POST /matches/generate/{round_id}`, `GET/POST /matches/{id}/result` |
| Ranking | `GET /ranking/`, `GET /ranking/me` |

El detalle completo (parámetros, respuestas y permisos) está en `/docs`.

## Despliegue

- **Backend en Render:** servicio web con directorio raíz `backend/`, comando de instalación `pip install -r requirements.txt` y comando de inicio `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Variables de entorno: `DATABASE_URL` (connection pooler de Supabase) y `SECRET_KEY`.
- **Frontend en Vercel:** se compila con `ng build`; el `apiUrl` de producción apunta al backend de Render.
- **CORS:** `backend/app/main.py` acepta `http://localhost:4200` y las URL del proyecto en Vercel (incluidas las de preview) mediante `allow_origin_regex`.

## Seguridad

- **Nunca subas el `.env`** ni los archivos `.env.*`: están en el `.gitignore`. Las credenciales y la `SECRET_KEY` se configuran como variables de entorno en Render.
- El primer administrador de producción debe crearse con una contraseña fuerte. No uses las cuentas de demostración en producción.
- Desactivar una cuenta surte efecto de inmediato: la API revalida al usuario en cada petición.

## Documentación

En la carpeta `docs/` están el documento de requisitos y el diseño del juego.
