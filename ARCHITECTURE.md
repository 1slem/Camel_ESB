# 🏛️ Architecture Technique - ESB Camel

## 📐 Vue d'ensemble de l'architecture

Ce document décrit en détail l'architecture technique du projet ESB, les choix de conception, et les patterns d'intégration utilisés.

---

## 🎯 Objectifs architecturaux

### Principes de conception

1. **Découplage** : Les systèmes client et fournisseur ne se connaissent pas directement
2. **Transformation** : Conversion automatique entre formats hétérogènes (XML ↔ JSON)
3. **Validation** : Garantie de la qualité des données via schéma XSD
4. **Extensibilité** : Facilité d'ajout de nouvelles routes et transformations
5. **Observabilité** : Logs détaillés à chaque étape du pipeline

---

## 🔄 Flux de données détaillé

### Diagramme de séquence

```
Client          ESB Camel           XSD Validator    XSLT Engine      Supplier
  |                |                      |               |              |
  |--SOAP/XML----->|                      |               |              |
  |                |                      |               |              |
  |                |--Validate----------->|               |              |
  |                |<--Valid/Invalid------|               |              |
  |                |                      |               |              |
  |                |--Transform---------------------->|   |              |
  |                |<--JSON---------------------------|   |              |
  |                |                      |               |              |
  |                |--Add Timestamp-----------------------|              |
  |                |                      |               |              |
  |                |--HTTP POST JSON----------------------|------------->|
  |                |                      |               |              |
  |                |<--200 OK---------------------------------|----------|
  |<--Response-----|                      |               |              |
```

### Étapes du pipeline

#### 1. Réception SOAP/XML
- **Endpoint** : `http://localhost:8080/OrderService`
- **Protocole** : SOAP over HTTP
- **Format** : XML avec enveloppe SOAP
- **Composant** : Apache CXF

```java
from("cxf://http://0.0.0.0:8080/OrderService?serviceClass=com.example.camel.OrderService")
```

#### 2. Validation XSD
- **Schéma** : `schemas/order.xsd`
- **Validateur** : Camel Validator Component
- **Action en cas d'erreur** : Rejet avec message d'erreur

```java
.to("validator:schemas/order.xsd")
```

**Schéma XSD** :
```xml
<xs:element name="order">
  <xs:complexType>
    <xs:sequence>
      <xs:element name="id" type="xs:string"/>
      <xs:element name="customer">...</xs:element>
      <xs:element name="items">...</xs:element>
    </xs:sequence>
  </xs:complexType>
</xs:element>
```

#### 3. Transformation XSLT
- **Template** : `xslt/order-to-json.xsl`
- **Entrée** : XML (élément `<order>`)
- **Sortie** : JSON (texte brut)
- **Moteur** : Saxon XSLT Processor

```java
.to("xslt:xslt/order-to-json.xsl")
```

**Exemple de transformation** :
```xml
<!-- Entrée XML -->
<order>
  <id>123</id>
  <customer>
    <name>Jean</name>
    <email>jean@example.com</email>
  </customer>
  <items>
    <item>
      <sku>ABC</sku>
      <qty>2</qty>
    </item>
  </items>
</order>
```

```json
// Sortie JSON
{
  "id": "123",
  "customer": {
    "name": "Jean",
    "email": "jean@example.com"
  },
  "items": [
    {"sku": "ABC", "qty": 2}
  ]
}
```

#### 4. Ajout du timestamp
- **Composant** : Supplier Flask App
- **Champ ajouté** : `orderDate`
- **Format** : ISO 8601 (`2025-11-02T14:30:45.123456`)

```python
if 'orderDate' not in order:
    order['orderDate'] = datetime.now().isoformat()
```

#### 5. Routage vers Supplier
- **Endpoint** : `http://localhost:5000/ingest`
- **Méthode** : HTTP POST
- **Content-Type** : `application/json`

```java
.setHeader("Content-Type", constant("application/json"))
.to("http://localhost:5000/ingest")
```

#### 6. Stockage et affichage
- **Stockage** : Fichier JSON (`orders.json`)
- **Dashboard** : Interface web temps réel
- **Rafraîchissement** : Manuel ou auto (5s)

---

## 🧩 Composants détaillés

### 1. ESB Apache Camel (camel-esb/)

#### Structure du projet

```
camel-esb/
├── src/main/java/com/example/camel/
│   ├── CamelEsbApplication.java    # Application Spring Boot
│   └── OrderRoute.java             # Définition de la route Camel
├── src/main/resources/
│   ├── schemas/order.xsd           # Schéma de validation
│   └── xslt/order-to-json.xsl      # Template de transformation
└── pom.xml                         # Configuration Maven
```

#### Dépendances clés

```xml
<dependencies>
  <!-- Spring Boot + Camel -->
  <dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-spring-boot-starter</artifactId>
    <version>3.18.0</version>
  </dependency>
  
  <!-- Support SOAP/CXF -->
  <dependency>
    <groupId>org.apache.camel</groupId>
    <artifactId>camel-cxf</artifactId>
    <version>3.18.0</version>
  </dependency>
  
  <!-- Validation XSD -->
  <dependency>
    <groupId>org.apache.camel</groupId>
    <artifactId>camel-validator</artifactId>
  </dependency>
  
  <!-- Transformation XSLT -->
  <dependency>
    <groupId>org.apache.camel</groupId>
    <artifactId>camel-xslt</artifactId>
  </dependency>
</dependencies>
```

#### Route Camel (OrderRoute.java)

```java
@Component
public class OrderRoute extends RouteBuilder {
    @Override
    public void configure() throws Exception {
        from("cxf://http://0.0.0.0:8080/OrderService?serviceClass=com.example.camel.OrderService")
            .routeId("order-soap-route")
            .log("Received order message")
            .to("validator:schemas/order.xsd")
            .log("XML validated")
            .to("xslt:xslt/order-to-json.xsl")
            .log("Transformed to JSON: ${body}")
            .setHeader("Content-Type", constant("application/json"))
            .to("http://localhost:5000/ingest")
            .log("Forwarded to supplier: ${header.CamelHttpResponseCode}");
    }
}
```

**Caractéristiques** :
- ✅ Route unique avec ID `order-soap-route`
- ✅ Logs à chaque étape pour traçabilité
- ✅ Gestion automatique des erreurs par Camel
- ✅ Headers HTTP configurés pour JSON

---

### 2. Service Supplier (supplier/)

#### Structure

```
supplier/
├── app.py              # API Flask + logique métier
├── index.html          # Dashboard web
├── orders.json         # Base de données JSON
└── requirements.txt    # Dépendances Python
```

#### API REST (app.py)

**Endpoints** :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Affiche le dashboard HTML |
| `/orders` | GET | Retourne toutes les commandes (JSON) |
| `/ingest` | POST | Reçoit et stocke une nouvelle commande |

**Code clé** :

```python
@app.route('/ingest', methods=['POST'])
def ingest():
    # Récupération de la commande JSON
    order = request.get_json()
    
    # Ajout du timestamp si absent
    if 'orderDate' not in order:
        order['orderDate'] = datetime.now().isoformat()
    
    # Chargement des commandes existantes
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    # Ajout de la nouvelle commande
    data.append(order)
    
    # Sauvegarde
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({'status': 'ok', 'stored': True}), 201
```

#### Dashboard Web (index.html)

**Fonctionnalités** :
- 📊 Affichage des commandes en cartes
- 🔄 Rafraîchissement manuel ou automatique (5s)
- 📅 Affichage de la date de commande formatée
- 🎨 Interface responsive et moderne

**Code JavaScript clé** :

```javascript
function refreshOrders() {
    fetch('http://localhost:5000/orders')
        .then(response => response.json())
        .then(orders => {
            orders.reverse().forEach(order => {
                // Formatage de la date
                let orderDate = new Date(order.orderDate).toLocaleString('fr-FR');
                
                // Création de la carte de commande
                orderCard.innerHTML = `
                    <div class="order-header">
                        <strong>Commande:</strong> ${order.id}<br>
                        <strong>Client:</strong> ${order.customer.name}<br>
                        <strong>Date:</strong> ${orderDate}
                    </div>
                    ...
                `;
            });
        });
}
```

---

### 3. Client (client/)

#### Interface Web (index.html)

- Formulaire de saisie de commande
- Génération automatique de SOAP/XML
- Envoi via Fetch API
- Affichage des réponses

#### Script Python (send_order.py)

```python
import requests

soap_envelope = '''<?xml version='1.0' encoding='UTF-8'?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <order>
            <id>TEST-001</id>
            ...
        </order>
    </soapenv:Body>
</soapenv:Envelope>'''

response = requests.post(
    'http://localhost:8080/OrderService',
    data=soap_envelope,
    headers={'Content-Type': 'text/xml'}
)
```

---

## 📊 Patterns d'intégration utilisés

### 1. Message Translator
**Problème** : Systèmes utilisant des formats différents (XML vs JSON)  
**Solution** : Transformation XSLT automatique  
**Implémentation** : `order-to-json.xsl`

### 2. Message Validator
**Problème** : Garantir la qualité des données entrantes  
**Solution** : Validation contre schéma XSD  
**Implémentation** : `camel-validator` + `order.xsd`

### 3. Content Enricher
**Problème** : Ajouter des métadonnées (date de commande)  
**Solution** : Enrichissement dans le Supplier  
**Implémentation** : Ajout de `orderDate` en Python

### 4. Message Router
**Problème** : Diriger les messages vers le bon destinataire  
**Solution** : Route Camel avec endpoint HTTP  
**Implémentation** : `.to("http://localhost:5000/ingest")`

### 5. Canonical Data Model
**Problème** : Multiples formats de données  
**Solution** : Format JSON standardisé comme modèle canonique  
**Implémentation** : Structure JSON commune

---

## 🔒 Sécurité et gestion des erreurs

### Validation des données
- ✅ Validation XSD stricte
- ✅ Vérification des types de contenu
- ✅ Gestion des données manquantes

### Gestion des erreurs
- ❌ Validation échouée → Rejet avec erreur 400
- ❌ Transformation échouée → Log + erreur 500
- ❌ Supplier indisponible → Retry automatique (Camel)

### Logs et traçabilité
```
[INFO] Received order message
[INFO] XML validated
[INFO] Transformed to JSON: {"id":"123",...}
[INFO] Forwarded to supplier: 201
```

---

## 🚀 Performance et scalabilité

### Optimisations
- **Camel** : Thread pools configurables
- **Flask** : Mode production avec Gunicorn
- **JSON** : Parsing optimisé

### Limites actuelles
- Stockage fichier (non scalable)
- Pas de cache
- Pas de load balancing

### Améliorations possibles
- 💾 Base de données (PostgreSQL, MongoDB)
- 🔄 Message Queue (RabbitMQ, Kafka)
- ⚖️ Load Balancer (Nginx)
- 📊 Monitoring (Prometheus, Grafana)

---

## 🔧 Configuration et déploiement

### Variables d'environnement

```bash
# ESB Camel
CAMEL_PORT=8080
SUPPLIER_URL=http://localhost:5000/ingest

# Supplier
FLASK_PORT=5000
DATA_FILE=orders.json
```

### Déploiement Docker (futur)

```dockerfile
# ESB
FROM openjdk:11
COPY target/camel-esb.jar /app.jar
CMD ["java", "-jar", "/app.jar"]

# Supplier
FROM python:3.9
COPY supplier/ /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

---

## 📚 Références

- [Apache Camel Documentation](https://camel.apache.org/manual/)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [XSLT 1.0 Specification](https://www.w3.org/TR/xslt-10/)
- [XML Schema (XSD) Tutorial](https://www.w3schools.com/xml/schema_intro.asp)

