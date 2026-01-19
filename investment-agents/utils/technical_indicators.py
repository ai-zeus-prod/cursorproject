"""
Technical Indicators Calculator
Uses pandas-ta for technical analysis
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, Optional
from loguru import logger


class TechnicalIndicators:
    """Calculate technical indicators for stock price data"""

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
            df['ma_50'] = ta.sma(df['close'], length=50)
            df['ma_200'] = ta.sma(df['close'], length=200)
            df['ema_20'] = ta.ema(df['close'], length=20)

            # RSI
            df['rsi'] = ta.rsi(df['close'], length=14)

            # MACD
            macd = ta.macd(df['close'])
            if macd is not None and not macd.empty:
                df['macd'] = macd.iloc[:, 0]
                df['macd_signal'] = macd.iloc[:, 1]
                df['macd_histogram'] = macd.iloc[:, 2]

            # Bollinger Bands
            bbands = ta.bbands(df['close'], length=20, std=2)
            if bbands is not None and not bbands.empty:
                df['bollinger_upper'] = bbands.iloc[:, 0]
                df['bollinger_mid'] = bbands.iloc[:, 1]
                df['bollinger_lower'] = bbands.iloc[:, 2]

            # Volume indicators
            df['volume_sma_20'] = ta.sma(df['volume'], length=20)
            df['volume_ratio'] = df['volume'] / df['volume_sma_20']

            # ATR (Average True Range) - for volatility
            df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)

            # Stochastic Oscillator
            stoch = ta.stoch(df['high'], df['low'], df['close'])
            if stoch is not None and not stoch.empty:
                df['stoch_k'] = stoch.iloc[:, 0]
                df['stoch_d'] = stoch.iloc[:, 1]

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
