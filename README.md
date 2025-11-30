# 🚀 Projet ESB (Enterprise Service Bus) - Démonstration

## 📋 Vue d'ensemble

Ce projet démontre une architecture **ESB (Enterprise Service Bus)** complète pour l'intégration de systèmes hétérogènes. Il illustre comment transformer et router des messages entre différents formats (XML/SOAP vers JSON) en utilisant Apache Camel et des technologies modernes.

### 🎯 Objectif du projet

Créer un pipeline d'intégration qui :
1. ✅ Reçoit des commandes au format **SOAP/XML**
2. ✅ Valide les données contre un **schéma XSD**
3. ✅ Transforme XML en **JSON** via **XSLT**
4. ✅ Ajoute automatiquement la **date de commande**
5. ✅ Route les messages vers un système fournisseur
6. ✅ Affiche les commandes dans un **tableau de bord web**

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │  SOAP   │     ESB      │  JSON   │  Supplier   │
│  (Web/CLI)  │ ──────> │ Apache Camel │ ──────> │   Service   │
│             │   XML   │  Port 8080   │  +Date  │  Port 5000  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │                         │
                              ▼                         ▼
                        ┌──────────┐              ┌──────────┐
                        │   XSD    │              │Dashboard │
                        │Validation│              │   Web    │
                        └──────────┘              └──────────┘
                              │
                              ▼
                        ┌──────────┐
                        │   XSLT   │
                        │Transform │
                        └──────────┘
```

### 🔄 Flux de données détaillé

1. **Client** → Envoie une commande SOAP/XML
2. **ESB** → Reçoit et valide contre `order.xsd`
3. **ESB** → Transforme XML en JSON via `order-to-json.xsl`
4. **ESB** → Route le JSON vers le Supplier
5. **Supplier** → Ajoute la date de commande (timestamp)
6. **Supplier** → Stocke dans `orders.json`
7. **Dashboard** → Affiche les commandes en temps réel

---

## 📁 Structure du projet

```
store/
├── camel-esb/              # ESB principal (Apache Camel + Spring Boot)
│   ├── src/main/java/
│   │   └── com/example/camel/
│   │       ├── CamelEsbApplication.java    # Point d'entrée Spring Boot
│   │       └── OrderRoute.java             # Route Camel (validation + transformation)
│   ├── src/main/resources/
│   │   ├── schemas/
│   │   │   └── order.xsd                   # Schéma de validation XML
│   │   └── xslt/
│   │       └── order-to-json.xsl           # Transformation XML → JSON
│   └── pom.xml                             # Dépendances Maven
│
├── supplier/               # Service fournisseur (Python Flask)
│   ├── app.py             # API REST + ajout timestamp
│   ├── index.html         # Dashboard web avec date de commande
│   ├── orders.json        # Base de données JSON
│   └── requirements.txt   # Dépendances Python
│
├── client/                # Client de test
│   ├── index.html         # Interface web pour envoyer des commandes
│   └── send_order.py      # Script Python CLI
│
├── python-esb/            # ESB alternatif en Python (même fonctionnalité)
│   ├── esb.py            # Implémentation Flask de l'ESB
│   └── requirements.txt
│
└── test-order.xml         # Exemple de commande SOAP
```

---

## 🛠️ Technologies utilisées

### Backend ESB (Java)
- **Apache Camel 3.18.0** - Framework d'intégration
- **Spring Boot 2.7.12** - Framework d'application
- **Apache CXF** - Support SOAP/Web Services
- **XSLT** - Transformation XML vers JSON
- **XSD** - Validation de schéma XML

### Backend Supplier (Python)
- **Flask** - Framework web léger
- **Flask-CORS** - Support des requêtes cross-origin
- **JSON** - Stockage des données

### Frontend
- **HTML5/CSS3** - Interface utilisateur
- **JavaScript Vanilla** - Logique client
- **Fetch API** - Requêtes HTTP asynchrones

---

## 🚀 Installation et démarrage

### Prérequis

- **Java 11+** (pour l'ESB Camel)
- **Maven 3.6+** (pour build Java)
- **Python 3.8+** (pour Supplier et Client)
- **pip** (gestionnaire de paquets Python)

### 1️⃣ Démarrer le Supplier

```bash
cd supplier
pip install -r requirements.txt
python app.py
```
✅ Le supplier démarre sur `http://localhost:5000`

### 2️⃣ Démarrer l'ESB (Apache Camel)

```bash
cd camel-esb
mvn clean install
mvn spring-boot:run
```
✅ L'ESB démarre sur `http://localhost:8080`

### 3️⃣ Tester avec le Client Web

Ouvrez `client/index.html` dans votre navigateur et envoyez une commande.

### 4️⃣ Visualiser les commandes

Ouvrez `http://localhost:5000` pour voir le tableau de bord avec les commandes et leurs dates.

---

## 📊 Exemple de commande

### Format XML (entrée)

```xml
<?xml version='1.0' encoding='UTF-8'?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <order>
            <id>ORD-001</id>
            <customer>
                <name>Jean Dupont</name>
                <email>jean.dupont@example.com</email>
            </customer>
            <items>
                <item>
                    <sku>LAPTOP-HP-15</sku>
                    <qty>2</qty>
                </item>
            </items>
        </order>
    </soapenv:Body>
</soapenv:Envelope>
```

### Format JSON (sortie avec date)

```json
{
  "id": "ORD-001",
  "customer": {
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com"
  },
  "items": [
    {
      "sku": "LAPTOP-HP-15",
      "qty": 2
    }
  ],
  "orderDate": "2025-11-02T14:30:45.123456"
}
```

---

## 🔍 Fonctionnalités clés

### ✨ Validation XML
- Validation stricte contre le schéma XSD
- Rejet des messages malformés
- Messages d'erreur détaillés

### 🔄 Transformation XSLT
- Conversion XML → JSON automatique
- Préservation de la structure des données
- Support des listes d'items

### 📅 Horodatage automatique
- Ajout de la date de passage de commande
- Format ISO 8601 (compatible international)
- Affichage formaté en français dans le dashboard

### 📊 Dashboard en temps réel
- Rafraîchissement manuel ou automatique (5s)
- Affichage des dernières commandes en premier
- Informations complètes : ID, client, items, date

---

## 🧪 Tests

### Test avec cURL

```bash
curl -X POST http://localhost:8080/OrderService \
  -H "Content-Type: text/xml" \
  -d @test-order.xml
```

### Test avec le script Python

```bash
cd client
python send_order.py
```

---

## 🔧 Configuration

### Ports utilisés
- **8080** : ESB Apache Camel
- **5000** : Supplier Service + Dashboard

### Fichiers de configuration
- `camel-esb/pom.xml` : Dépendances et versions
- `camel-esb/src/main/resources/schemas/order.xsd` : Schéma de validation
- `camel-esb/src/main/resources/xslt/order-to-json.xsl` : Règles de transformation

---

## 📚 Concepts démontrés

### 🎓 Patterns d'intégration
- **Message Transformation** : XML → JSON
- **Content-Based Routing** : Routage basé sur le contenu
- **Message Validation** : Validation XSD
- **Canonical Data Model** : Format JSON standardisé

### 🏛️ Architecture
- **ESB (Enterprise Service Bus)** : Médiation entre systèmes
- **SOA (Service-Oriented Architecture)** : Services découplés
- **API REST** : Communication HTTP/JSON
- **SOAP Web Services** : Services XML

---

## 🆚 Comparaison des implémentations

| Caractéristique | Camel ESB (Java) | Python ESB |
|----------------|------------------|------------|
| Framework | Apache Camel + Spring Boot | Flask + lxml |
| Performance | ⭐⭐⭐⭐⭐ Haute | ⭐⭐⭐ Moyenne |
| Scalabilité | ⭐⭐⭐⭐⭐ Excellente | ⭐⭐⭐ Bonne |
| Facilité | ⭐⭐⭐ Moyenne | ⭐⭐⭐⭐⭐ Facile |
| Production | ✅ Recommandé | ⚠️ Prototypage |

---

## 🎯 Cas d'usage

Ce projet peut être adapté pour :
- 🛒 **E-commerce** : Intégration commandes → ERP
- 🏭 **Industrie** : Échange de données B2B
- 🏥 **Santé** : Intégration systèmes hospitaliers
- 🏦 **Finance** : Transformation messages bancaires

---

## 📝 Licence

Ce projet est à but éducatif et de démonstration.

---

## 👥 Auteur

Projet de démonstration ESB - Architecture d'intégration d'entreprise

---

## 🔗 Ressources

- [Apache Camel Documentation](https://camel.apache.org/)
- [Spring Boot Guide](https://spring.io/guides)
- [XSLT Tutorial](https://www.w3schools.com/xml/xsl_intro.asp)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)

