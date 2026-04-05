#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
ENV_EXAMPLE_FILE="$ROOT_DIR/.env.example"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
BUILD_MODE="none"

print_usage() {
  cat <<'EOF'
Uso: bash scripts/start-services.sh [opcion]

Opciones:
  --up        Solo levantar servicios
  --build     Construir imagenes antes de levantar servicios
  --no-cache  Construir imagenes sin cache antes de levantar servicios
  --help      Mostrar esta ayuda
EOF
}

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --up)
        BUILD_MODE="none"
        ;;
      --build)
        BUILD_MODE="build"
        ;;
      --no-cache)
        BUILD_MODE="no-cache"
        ;;
      --help|-h)
        print_usage
        exit 0
        ;;
      *)
        echo "Opcion no soportada: $1"
        print_usage
        exit 1
        ;;
    esac
    shift
  done
}

ensure_docker_ready() {
  if docker info >/dev/null 2>&1; then
    return 0
  fi

  case "$(uname -s)" in
    Linux)
      if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start docker >/dev/null 2>&1 || true
      elif command -v service >/dev/null 2>&1; then
        sudo service docker start >/dev/null 2>&1 || true
      fi
      ;;
    Darwin)
      if command -v open >/dev/null 2>&1; then
        open -a Docker >/dev/null 2>&1 || true
      fi
      ;;
  esac

  for _ in $(seq 1 30); do
    if docker info >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done

  echo "Docker no esta disponible. Inicia Docker y vuelve a intentar."
  exit 1
}

ensure_env_file() {
  if [ -f "$ENV_FILE" ]; then
    return 0
  fi

  if [ -f "$ENV_EXAMPLE_FILE" ]; then
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    echo "Se creo $ENV_FILE a partir de .env.example"
    return 0
  fi

  echo "Falta $ENV_FILE y no existe .env.example"
  exit 1
}

read_env_value() {
  local key="$1"
  local default_value="$2"
  local raw_value

  raw_value="$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -n 1 | cut -d '=' -f 2- || true)"
  if [ -z "$raw_value" ]; then
    echo "$default_value"
    return 0
  fi

  raw_value="${raw_value%\"}"
  raw_value="${raw_value#\"}"
  echo "$raw_value"
}

port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn "( sport = :$port )" 2>/dev/null | tail -n +2 | grep -q .
    return $?
  fi

  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  fi

  return 1
}

allow_running_stack_port() {
  local service_name="$1"
  docker compose ps --status running --services 2>/dev/null | grep -qx "$service_name"
}

check_ports() {
  local api_port="$1"
  local frontend_port="$2"

  if port_in_use "$api_port" && ! allow_running_stack_port "aqrisk-api"; then
    echo "El puerto $api_port ya esta en uso. Ajusta AQRISK_API_PORT en .env antes de continuar."
    exit 1
  fi

  if port_in_use "$frontend_port" && ! allow_running_stack_port "aqrisk-frontend"; then
    echo "El puerto $frontend_port ya esta en uso. Ajusta AQRISK_FRONTEND_PORT en .env antes de continuar."
    exit 1
  fi
}

compose_build() {
  local cache_args=("$@")
  docker compose build "${cache_args[@]}"
}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker no esta instalado o no esta en PATH."
  exit 1
fi

parse_args "$@"
ensure_docker_ready
ensure_env_file

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "No se encontro docker-compose.yml en $ROOT_DIR"
  exit 1
fi

cd "$ROOT_DIR"

API_PORT="$(read_env_value "AQRISK_API_PORT" "18010")"
FRONTEND_PORT="$(read_env_value "AQRISK_FRONTEND_PORT" "18080")"

check_ports "$API_PORT" "$FRONTEND_PORT"

case "$BUILD_MODE" in
  build)
    compose_build
    ;;
  no-cache)
    compose_build --no-cache
    ;;
esac

docker compose up -d

echo "Servicios iniciados."
echo "API: http://localhost:$API_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Usa 'docker compose ps' para verificar el estado."
