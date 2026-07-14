import httpx
from config import API_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.access_token = None
        self.refresh_token = None

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def inscrire(self, data: dict) -> dict:
        """Inscription publique d'un citoyen — sans authentification."""
        try:
            r = httpx.post(f"{self.base_url}/auth/inscription", json=data, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def login(self, email: str, password: str) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/auth/login", json={"email": email, "password": password}, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def verify_mfa(self, email: str, code: str) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/auth/verify-mfa", json={"email": email, "code": code}, timeout=10)
            data = r.json()
            if data.get("access"):
                self.access_token = data["access"]
                self.refresh_token = data["refresh"]
            return data
        except Exception as e:
            return {"error": str(e)}

    def get_me(self) -> dict:
        try:
            r = httpx.get(f"{self.base_url}/auth/me", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_caveaux_geojson(self) -> dict:
        try:
            r = httpx.get(f"{self.base_url}/caveaux/geojson", timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_zones(self) -> list:
        try:
            r = httpx.get(f"{self.base_url}/terrain/zones", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return []

    def get_reservations(self, statut: str = None) -> list:
        try:
            params = {}
            if statut:
                params["statut"] = statut
            r = httpx.get(f"{self.base_url}/reservations/", headers=self._headers(), params=params, timeout=10)
            return r.json()
        except Exception as e:
            return []

    def creer_reservation(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/reservations/", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def valider_reservation(self, reservation_id: int, notes: str = "") -> dict:
        try:
            r = httpx.post(f"{self.base_url}/reservations/{reservation_id}/valider", json={"notes_admin": notes}, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def refuser_reservation(self, reservation_id: int, motif: str) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/reservations/{reservation_id}/refuser", json={"motif_refus": motif}, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_paiements(self, statut: str = None) -> list:
        try:
            params = {}
            if statut:
                params["statut"] = statut
            r = httpx.get(f"{self.base_url}/paiements/", headers=self._headers(), params=params, timeout=10)
            return r.json()
        except Exception as e:
            return []

    def enregistrer_paiement(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/paiements/", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_statistiques(self) -> dict:
        try:
            r = httpx.get(f"{self.base_url}/reporting/statistiques", timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_concessions(self, statut: str = None) -> list:
        try:
            params = {}
            if statut:
                params["statut"] = statut
            r = httpx.get(f"{self.base_url}/concessions/", headers=self._headers(), params=params, timeout=10)
            return r.json()
        except Exception as e:
            return []

    def renouveler_concession(self, concession_id: int, montant: float, notes: str = "") -> dict:
        try:
            r = httpx.post(f"{self.base_url}/concessions/{concession_id}/renouveler", json={"montant_xaf": montant, "notes": notes}, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def resilier_concession(self, concession_id: int, motif: str) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/concessions/{concession_id}/resilier", json={"motif_resiliation": motif}, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_utilisateurs(self) -> list:
        try:
            r = httpx.get(f"{self.base_url}/admin/utilisateurs", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return []

    def creer_utilisateur(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/admin/utilisateurs", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def modifier_utilisateur(self, user_id: int, data: dict) -> dict:
        try:
            r = httpx.patch(f"{self.base_url}/admin/utilisateurs/{user_id}", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def supprimer_utilisateur(self, user_id: int) -> dict:
        try:
            r = httpx.delete(f"{self.base_url}/admin/utilisateurs/{user_id}", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_exhumations(self, statut: str = None) -> list:
        try:
            params = {}
            if statut:
                params["statut"] = statut
            r = httpx.get(f"{self.base_url}/exhumations/", headers=self._headers(), params=params, timeout=10)
            return r.json()
        except Exception as e:
            return []

    def creer_exhumation(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/exhumations/", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def valider_exhumation(self, exhumation_id: int, notes: str = "") -> dict:
        try:
            r = httpx.post(
                f"{self.base_url}/exhumations/{exhumation_id}/valider",
                json={"notes": notes},
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def refuser_exhumation(self, exhumation_id: int, motif: str) -> dict:
        try:
            r = httpx.post(
                f"{self.base_url}/exhumations/{exhumation_id}/refuser",
                json={"motif_refus": motif},
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def deconnecter(self):
        self.access_token = None
        self.refresh_token = None
    
    def changer_statut_caveau(self, caveau_id: int, statut: str) -> dict:
        try:
            r = httpx.patch(
                f"{self.base_url}/caveaux/{caveau_id}/statut",
                params={"statut": statut},
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}
    
    
    def get_zones(self) -> list:
        try:
            r = httpx.get(f"{self.base_url}/terrain/zones", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return []

    def get_blocs(self) -> list:
        try:
            r = httpx.get(f"{self.base_url}/terrain/blocs", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return []

    def creer_zone(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/terrain/zones", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def creer_bloc(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/terrain/blocs", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def creer_caveau(self, data: dict) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/caveaux/", json=data, headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}     
    
    def envoyer_alertes_expiration(self) -> dict:
        try:
            r = httpx.post(f"{self.base_url}/concessions/alertes-expiration", headers=self._headers(), timeout=15)
            return r.json()
        except Exception as e:
            return {"error": str(e)}
        
    def url_autorisation_exhumation(self, exhumation_id: int) -> str:
        return f"{self.base_url}/exhumations/{exhumation_id}/autorisation-pdf"  
    
    
    def effectuer_exhumation(self, exhumation_id: int) -> dict:
        try:
            r = httpx.post(
                f"{self.base_url}/exhumations/{exhumation_id}/effectuer",
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}         

    def get_statistiques_terrain(self) -> dict:
        try:
            r = httpx.get(f"{self.base_url}/terrain/cimetiere/statistiques", headers=self._headers(), timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def configurer_cimetiere(self, data: dict) -> dict:
        try:
            r = httpx.patch(
                f"{self.base_url}/terrain/cimetiere/configuration",
                params=data,
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}
    def get_solde_reservation(self, reservation_id: int) -> dict:
        try:
            r = httpx.get(
                f"{self.base_url}/paiements/solde/{reservation_id}",
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}    
    
    def simuler_mobile_money(self, reservation_id: int, montant: float, canal: str, telephone: str) -> dict:
        try:
            r = httpx.post(
                f"{self.base_url}/paiements/simuler-mobile-money",
                params={
                    "reservation_id": reservation_id,
                    "montant": montant,
                    "canal": canal,
                    "telephone": telephone,
                },
                headers=self._headers(),
                timeout=10,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}    

# Instance globale
client = APIClient()