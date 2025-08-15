# Rôle `mongo_replicaset`

Installe et configure un replica set MongoDB (N nœuds) multi-OS. Gère l’auth, keyFile, comptes admin & monitoring.

## Inventaire

```ini
[mongodb]
mongo1 ansible_host=10.0.0.11
mongo2 ansible_host=10.0.0.12
mongo3 ansible_host=10.0.0.13
```

## Déploiement initial

```yaml
- hosts: mongodb
  become: true
  roles:
    - role: mongo_replicaset
      vars:
        mongo_major: "7.0"
        mongo_version: ""     # ou p.ex. "7.0.12"
        mongo_replset_name: "rs-production"
        mongo_dbpath: "/data/mongo"
        mongo_bind_ip: ["0.0.0.0"]
        mongo_admin_user: "admin"
        mongo_admin_pass: !vault |
          <VAULTED_STRING>
        mongo_monitor_user: "monitor"
        mongo_monitor_pass: !vault |
          <VAULTED_STRING>
```

## Upgrade sans coupure (rolling)

> Pré-requis : replica set ≥ 3 nœuds, santé OK (PRIMARY + SECONDARYs), write concern `majority` côté applis pendant la fenêtre de maintenance.

Playbook d’upgrade (exemple) :

```yaml
- hosts: mongodb
  become: true
  serial: 1   # clé pour éviter la coupure
  vars:
    mongo_rolling_upgrade: true
    mongo_target_version: "7.0.12"   # vide => latest du dépôt
    mongo_set_fcv_after_upgrade: false # passez à true pour tenter le bump FCV automatiquement
  roles:
    - role: mongo_replicaset
```

Étapes finales après upgrade **majeur** (ex: 6.0→7.0) :

1. Vérifier que le cluster est stable (PRIMARY élu, `rs.status()`).
2. Sur le PRIMARY, exécuter :
   ```bash
   mongosh --eval "db.adminCommand({ setFeatureCompatibilityVersion: '7.0' })"
   ```

## Variables clés

Voir `defaults/main.yml` pour toutes les options (TLS, ulimits, firewall, rolling upgrade...).

## Sécurité

- Stockez les mots de passe dans **Ansible Vault**.
- Restreignez les accès réseau au port 27017 (liste blanche des CIDR).

## Dépannage

- Logs: `/var/log/mongodb/mongod.log`
- État: `mongosh --eval 'rs.status()'`
