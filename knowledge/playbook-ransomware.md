## Playbook: Resposta a Ransomware
**Versão:** 2.1 | **Última atualização:** Jan 2025

### Fase 1 — Identificação (0-15 min)
1. Confirmar criptografia de arquivos via extensão anômala
2. Verificar nota de resgate (geralmente README.txt ou similar)
3. Identificar vetor de entrada via logs de autenticação
4. Identificar Patient Zero (primeiro sistema afetado)

### Fase 2 — Contenção (15-30 min)
1. **ISOLAR IMEDIATAMENTE** o(s) sistema(s) afetado(s) da rede
   - Desconectar cabo de rede OU desabilitar NIC via IPMI
   - NÃO desligar o sistema (preserva evidências em memória)
2. Bloquear comunicação com domínios/IPs do C2 no firewall
3. Suspender contas comprometidas no AD
4. Notificar: CISO, Jurídico, Comunicação

### Fase 3 — Erradicação
...