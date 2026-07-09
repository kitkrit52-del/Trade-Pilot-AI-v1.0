"""
Binance API Service Module
Handles all Binance exchange interactions for trading and market data
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import json
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class BinanceService:
    """
    Service for interacting with Binance API
    Supports spot trading, margin trading, and market data retrieval
    """
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Binance service with API credentials
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet if True (default: False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        if testnet:
            self.base_url = "https://testnet.binance.vision"
        else:
            self.base_url = self.BASE_URL
            
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature for request"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 signed: bool = False) -> Dict:
        """
        Make HTTP request to Binance API
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            params: Request parameters
            signed: Whether request requires signature
            
        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        if signed:
            params['timestamp'] = int(datetime.utcnow().timestamp() * 1000)
            query_string = urlencode(params)
            params['signature'] = self._generate_signature(query_string)
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, params=params)
            elif method == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance API request failed: {str(e)}")
            raise
    
    # ==================== Market Data Endpoints ====================
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Get ticker data for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Ticker data dictionary
        """
        params = {'symbol': symbol}
        return self._request("GET", "/api/v3/ticker/24hr", params)
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get order book for a symbol
        
        Args:
            symbol: Trading pair
            limit: Number of levels (default: 100, max: 5000)
            
        Returns:
            Order book data
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request("GET", "/api/v3/depth", params)
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500,
                   start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[List]:
        """
        Get candlestick data (klines)
        
        Args:
            symbol: Trading pair
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles (default: 500, max: 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of candles with OHLCV data
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
            
        return self._request("GET", "/api/v3/klines", params)
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """
        Get recent trades for a symbol
        
        Args:
            symbol: Trading pair
            limit: Number of trades (default: 500, max: 1000)
            
        Returns:
            List of recent trades
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request("GET", "/api/v3/trades", params)
    
    def get_avg_price(self, symbol: str) -> Dict:
        """
        Get average price for a symbol
        
        Args:
            symbol: Trading pair
            
        Returns:
            Average price data
        """
        params = {'symbol': symbol}
        return self._request("GET", "/api/v3/avgPrice", params)
    
    # ==================== Trading Endpoints ====================
    
    def create_order(self, symbol: str, side: str, order_type: str, 
                    quantity: float, price: Optional[float] = None,
                    stop_price: Optional[float] = None,
                    client_order_id: Optional[str] = None) -> Dict:
        """
        Create an order
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            order_type: LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT, etc.
            quantity: Order quantity
            price: Price per unit (required for LIMIT orders)
            stop_price: Stop price (required for STOP_LOSS orders)
            client_order_id: Custom order ID
            
        Returns:
            Order confirmation
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if price:
            params['price'] = price
        if stop_price:
            params['stopPrice'] = stop_price
        if client_order_id:
            params['newClientOrderId'] = client_order_id
        
        params['timeInForce'] = 'GTC' if order_type == 'LIMIT' else None
        
        return self._request("POST", "/api/v3/order", params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None,
                    client_order_id: Optional[str] = None) -> Dict:
        """
        Cancel an order
        
        Args:
            symbol: Trading pair
            order_id: Order ID (use either this or client_order_id)
            client_order_id: Client order ID
            
        Returns:
            Cancellation confirmation
        """
        params = {'symbol': symbol}
        
        if order_id:
            params['orderId'] = order_id
        elif client_order_id:
            params['origClientOrderId'] = client_order_id
        else:
            raise ValueError("Either order_id or client_order_id must be provided")
        
        return self._request("DELETE", "/api/v3/order", params, signed=True)
    
    def get_order(self, symbol: str, order_id: Optional[int] = None,
                 client_order_id: Optional[str] = None) -> Dict:
        """
        Get order details
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            client_order_id: Client order ID
            
        Returns:
            Order details
        """
        params = {'symbol': symbol}
        
        if order_id:
            params['orderId'] = order_id
        elif client_order_id:
            params['origClientOrderId'] = client_order_id
        else:
            raise ValueError("Either order_id or client_order_id must be provided")
        
        return self._request("GET", "/api/v3/order", params, signed=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders
        
        Args:
            symbol: Optional - filter by trading pair
            
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
            
        return self._request("GET", "/api/v3/openOrders", params, signed=True)
    
    def get_order_history(self, symbol: str, limit: int = 500) -> List[Dict]:
        """
        Get order history
        
        Args:
            symbol: Trading pair
            limit: Number of orders (max: 1000)
            
        Returns:
            List of orders
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request("GET", "/api/v3/allOrders", params, signed=True)
    
    # ==================== Account Endpoints ====================
    
    def get_account_info(self) -> Dict:
        """
        Get account information including balances
        
        Returns:
            Account information with balances
        """
        return self._request("GET", "/api/v3/account", signed=True)
    
    def get_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        """
        Get account balances
        
        Args:
            asset: Optional - filter by specific asset (e.g., 'BTC')
            
        Returns:
            Dictionary of asset balances
        """
        account_info = self.get_account_info()
        balances = {}
        
        for balance in account_info.get('balances', []):
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:  # Only include non-zero balances
                balances[balance['asset']] = {
                    'free': free,
                    'locked': locked,
                    'total': total
                }
        
        if asset:
            return balances.get(asset, {'free': 0, 'locked': 0, 'total': 0})
        
        return balances
    
    def get_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """
        Get user's trades for a symbol
        
        Args:
            symbol: Trading pair
            limit: Number of trades (max: 1000)
            
        Returns:
            List of user trades
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request("GET", "/api/v3/myTrades", params, signed=True)
    
    # ==================== Utility Methods ====================
    
    def get_exchange_info(self) -> Dict:
        """
        Get exchange information including trading rules
        
        Returns:
            Exchange information
        """
        return self._request("GET", "/api/v3/exchangeInfo")
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get trading rules for a specific symbol
        
        Args:
            symbol: Trading pair
            
        Returns:
            Symbol trading rules
        """
        info = self.get_exchange_info()
        for sym in info.get('symbols', []):
            if sym['symbol'] == symbol:
                return sym
        return None
    
    def calculate_trading_fees(self, symbol: str, quantity: float, 
                              price: float, is_buy: bool = True) -> Dict:
        """
        Calculate trading fees for an order
        
        Args:
            symbol: Trading pair
            quantity: Order quantity
            price: Order price
            is_buy: True for buy order, False for sell
            
        Returns:
            Fee information
        """
        order_value = quantity * price
        
        account = self.get_account_info()
        maker_fee = float(account.get('makerCommission', 10)) / 10000  # Basis points
        taker_fee = float(account.get('takerCommission', 10)) / 10000
        
        return {
            'order_value': order_value,
            'maker_fee_rate': maker_fee,
            'taker_fee_rate': taker_fee,
            'estimated_fee': order_value * taker_fee,  # Assume taker for safety
            'total_with_fees': order_value + (order_value * taker_fee)
        }
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("Binance service session closed")
