"""
Technical Indicators Calculator
Implements technical indicators using pure pandas/numpy
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from loguru import logger


class TechnicalIndicators:
    """Calculate technical indicators for stock price data"""

    @staticmethod
    def calculate_sma(series: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return series.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD indicator"""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {
            'macd': macd_line,
            'macd_signal': signal_line,
            'macd_histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return {
            'bb_upper': upper,
            'bb_middle': sma,
            'bb_lower': lower
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        return atr

    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        stoch_k = stoch_k.rolling(window=smooth_k).mean()
        stoch_d = stoch_k.rolling(window=smooth_d).mean()
        return {
            'stoch_k': stoch_k,
            'stoch_d': stoch_d
        }

    @staticmethod
    def calculate_all_indicators(price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for a price dataframe

        Args:
            price_df: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']

        Returns:
            DataFrame with additional indicator columns
        """
        try:
            df = price_df.copy()

            # Ensure we have enough data
            if len(df) < 200:
                logger.warning(f"Not enough data for complete technical analysis. Have {len(df)} rows, need 200+")

            # Moving Averages
            df['ma_50'] = TechnicalIndicators.calculate_sma(df['close'], 50)
            df['ma_200'] = TechnicalIndicators.calculate_sma(df['close'], 200)
            df['ema_20'] = TechnicalIndicators.calculate_ema(df['close'], 20)

            # RSI
            df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'], 14)

            # MACD
            macd = TechnicalIndicators.calculate_macd(df['close'])
            df['macd'] = macd['macd']
            df['macd_signal'] = macd['macd_signal']
            df['macd_histogram'] = macd['macd_histogram']

            # Bollinger Bands
            bbands = TechnicalIndicators.calculate_bollinger_bands(df['close'], 20, 2)
            df['bollinger_upper'] = bbands['bb_upper']
            df['bollinger_mid'] = bbands['bb_middle']
            df['bollinger_lower'] = bbands['bb_lower']

            # Volume indicators
            df['volume_sma_20'] = TechnicalIndicators.calculate_sma(df['volume'], 20)
            df['volume_ratio'] = df['volume'] / df['volume_sma_20']

            # ATR (Average True Range) - for volatility
            df['atr'] = TechnicalIndicators.calculate_atr(df, 14)

            # Stochastic Oscillator
            stoch = TechnicalIndicators.calculate_stochastic(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch['stoch_k']
            df['stoch_d'] = stoch['stoch_d']

            return df

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return price_df

    @staticmethod
    def get_latest_indicators(price_df: pd.DataFrame) -> Optional[Dict]:
        """
        Get the latest technical indicator values

        Returns a dictionary with the most recent values
        """
        try:
            df = TechnicalIndicators.calculate_all_indicators(price_df)

            if df.empty:
                return None

            latest = df.iloc[-1]

            indicators = {
                'date': latest.get('date'),
                'close': latest.get('close'),
                'ma_50': latest.get('ma_50'),
                'ma_200': latest.get('ma_200'),
                'ema_20': latest.get('ema_20'),
                'rsi': latest.get('rsi'),
                'macd': latest.get('macd'),
                'macd_signal': latest.get('macd_signal'),
                'macd_histogram': latest.get('macd_histogram'),
                'bollinger_upper': latest.get('bollinger_upper'),
                'bollinger_lower': latest.get('bollinger_lower'),
                'volume_sma_20': latest.get('volume_sma_20'),
                'volume_ratio': latest.get('volume_ratio'),
                'atr': latest.get('atr'),
                'stoch_k': latest.get('stoch_k'),
                'stoch_d': latest.get('stoch_d'),
            }

            # Remove None values
            indicators = {k: v for k, v in indicators.items() if pd.notna(v)}

            return indicators

        except Exception as e:
            logger.error(f"Error getting latest indicators: {str(e)}")
            return None

    @staticmethod
    def check_ma_trend(price_df: pd.DataFrame, days: int = 20) -> Dict:
        """
        Check if moving averages are trending up or down

        Returns:
            Dict with trend information for 50-day and 200-day MAs
        """
        try:
            df = price_df.copy()
            df['ma_50'] = ta.sma(df['close'], length=50)
            df['ma_200'] = ta.sma(df['close'], length=200)

            # Get recent MA values
            recent_df = df.tail(days)

            ma_50_trend = "up" if recent_df['ma_50'].iloc[-1] > recent_df['ma_50'].iloc[0] else "down"
            ma_200_trend = "up" if recent_df['ma_200'].iloc[-1] > recent_df['ma_200'].iloc[0] else "down"

            return {
                'ma_50_trending_up': ma_50_trend == "up",
                'ma_200_trending_up': ma_200_trend == "up",
                'price_above_ma_50': df['close'].iloc[-1] > df['ma_50'].iloc[-1] if pd.notna(df['ma_50'].iloc[-1]) else False,
                'price_above_ma_200': df['close'].iloc[-1] > df['ma_200'].iloc[-1] if pd.notna(df['ma_200'].iloc[-1]) else False,
                'golden_cross': df['ma_50'].iloc[-1] > df['ma_200'].iloc[-1] if pd.notna(df['ma_50'].iloc[-1]) and pd.notna(df['ma_200'].iloc[-1]) else False
            }

        except Exception as e:
            logger.error(f"Error checking MA trend: {str(e)}")
            return {}

    @staticmethod
    def detect_support_resistance(price_df: pd.DataFrame, window: int = 20) -> Dict:
        """
        Detect support and resistance levels using local minima/maxima

        Args:
            price_df: Price dataframe
            window: Window size for detecting local extrema

        Returns:
            Dict with support and resistance levels
        """
        try:
            df = price_df.copy().tail(100)  # Use last 100 days

            # Find local minima (support)
            local_min = df['low'].rolling(window=window, center=True).min()
            support_levels = df[df['low'] == local_min]['low'].unique()

            # Find local maxima (resistance)
            local_max = df['high'].rolling(window=window, center=True).max()
            resistance_levels = df[df['high'] == local_max]['high'].unique()

            # Get the most relevant levels (closest to current price)
            current_price = df['close'].iloc[-1]

            # Support: highest level below current price
            support_below = support_levels[support_levels < current_price]
            nearest_support = support_below.max() if len(support_below) > 0 else None

            # Resistance: lowest level above current price
            resistance_above = resistance_levels[resistance_levels > current_price]
            nearest_resistance = resistance_above.min() if len(resistance_above) > 0 else None

            return {
                'current_price': current_price,
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'support_levels': support_levels.tolist() if len(support_levels) > 0 else [],
                'resistance_levels': resistance_levels.tolist() if len(resistance_levels) > 0 else []
            }

        except Exception as e:
            logger.error(f"Error detecting support/resistance: {str(e)}")
            return {}

    @staticmethod
    def is_overbought_oversold(rsi: float) -> str:
        """
        Determine if stock is overbought, oversold, or neutral based on RSI

        Args:
            rsi: RSI value

        Returns:
            'overbought', 'oversold', or 'neutral'
        """
        if rsi >= 70:
            return 'overbought'
        elif rsi <= 30:
            return 'oversold'
        else:
            return 'neutral'

    @staticmethod
    def calculate_momentum_score(price_df: pd.DataFrame) -> float:
        """
        Calculate a momentum score (0-100) based on multiple factors

        Args:
            price_df: Price dataframe

        Returns:
            Score from 0-100
        """
        try:
            df = TechnicalIndicators.calculate_all_indicators(price_df)
            latest = df.iloc[-1]

            score = 50  # Start neutral

            # RSI (20 points)
            rsi = latest.get('rsi')
            if pd.notna(rsi):
                if 45 <= rsi <= 65:
                    score += 20  # Ideal range
                elif 40 <= rsi < 45 or 65 < rsi <= 70:
                    score += 10  # Acceptable
                elif rsi > 80 or rsi < 20:
                    score -= 20  # Extreme

            # Moving Average position (20 points)
            close = latest.get('close')
            ma_50 = latest.get('ma_50')
            ma_200 = latest.get('ma_200')

            if pd.notna(ma_50) and pd.notna(ma_200):
                if close > ma_50 > ma_200:
                    score += 20  # Strong uptrend
                elif close > ma_50:
                    score += 10  # Above 50-day
                elif close < ma_50 < ma_200:
                    score -= 20  # Downtrend

            # MACD (15 points)
            macd = latest.get('macd')
            macd_signal = latest.get('macd_signal')

            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal and macd > 0:
                    score += 15  # Bullish
                elif macd > macd_signal:
                    score += 8   # Turning bullish
                elif macd < macd_signal:
                    score -= 15  # Bearish

            # Volume (10 points)
            volume_ratio = latest.get('volume_ratio')
            if pd.notna(volume_ratio):
                if volume_ratio > 1.5:
                    score += 10  # High volume
                elif volume_ratio < 0.7:
                    score -= 5   # Low volume

            # Price vs Bollinger Bands (10 points)
            bb_upper = latest.get('bollinger_upper')
            bb_lower = latest.get('bollinger_lower')

            if pd.notna(bb_upper) and pd.notna(bb_lower):
                bb_position = (close - bb_lower) / (bb_upper - bb_lower)
                if 0.3 <= bb_position <= 0.7:
                    score += 10  # Middle of bands
                elif bb_position > 0.9:
                    score -= 10  # Near upper band (overbought)
                elif bb_position < 0.1:
                    score += 5   # Near lower band (potential bounce)

            # Ensure score is between 0 and 100
            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Error calculating momentum score: {str(e)}")
            return 50  # Return neutral on error
