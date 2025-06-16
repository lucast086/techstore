![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/lucast086/techstore?sort=semver)

# TechStore SaaS

## Versionado

Este proyecto sigue [Versionado Semántico (SemVer)](https://semver.org/lang/es/) y el flujo de trabajo Git Flow. Todas las reglas y convenciones están documentadas en `docs/versionado.md`.

- **Formato de versión:** `X.Y.Z` (Mayor.Menor.Parche)
- **Flujo Git:** main, develop, feature/*, release/*, hotfix/*
- **Commits:** Usar [Conventional Commits](https://www.conventionalcommits.org/)
- **Etiquetas:** Automáticas al finalizar releases/hotfixes

### Uso del script de versionado

Ejemplo de comandos:
```bash
./scripts/version.sh init
./scripts/version.sh feature start auth-system
./scripts/version.sh release start 1.0.0
./scripts/version.sh release finish 1.0.0
./scripts/version.sh current
```

Para más detalles, consulta `docs/versionado.md`.
