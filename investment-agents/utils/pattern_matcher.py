"""
Pattern Matcher - Identify chart patterns and compare to historical patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


class PatternMatcher:
    """Match current price patterns to historical successful patterns"""

    @staticmethod
    def normalize_series(series: pd.Series) -> np.ndarray:
        """Normalize a price series to 0-100 scale"""
        min_val = series.min()
        max_val = series.max()

        if max_val == min_val:
            return np.zeros(len(series))

        return ((series - min_val) / (max_val - min_val) * 100).values

    @staticmethod
    def detect_cup_and_handle(price_df: pd.DataFrame, window: int = 60) -> Optional[Dict]:
        """
        Detect cup and handle pattern

        Returns:
            Dict with pattern details if found, None otherwise
        """
        try:
            if len(price_df) < window:
                return None

            df = price_df.tail(window).copy()
            close_prices = df['close'].values

            # Normalize prices
            norm_prices = PatternMatcher.normalize_series(df['close'])

            # Find the lowest point (cup bottom)
            bottom_idx = np.argmin(close_prices[:int(window * 0.6)])
            bottom_price = close_prices[bottom_idx]

            # Check for cup formation (U-shape)
            left_side = close_prices[:bottom_idx]
            right_side = close_prices[bottom_idx:int(window * 0.7)]

            if len(left_side) < 5 or len(right_side) < 5:
                return None

            # Cup should have higher prices on both sides
            left_high = left_side.max()
            right_high = right_side.max()

            # Cup bottom should be significantly lower
            cup_depth = min(left_high, right_high) - bottom_price
            relative_depth = cup_depth / bottom_price

            if relative_depth < 0.12 or relative_depth > 0.35:
                return None  # Not a proper cup depth

            # Check for handle (slight pullback after right side)
            handle_start = int(window * 0.7)
            if handle_start >= len(close_prices) - 5:
                return None

            handle_prices = close_prices[handle_start:]
            handle_low = handle_prices.min()
            handle_high = handle_prices.max()

            # Handle should be shallower than cup
            handle_depth = handle_high - handle_low
            if handle_depth > cup_depth * 0.5:
                return None

            # Current price should be near handle high (potential breakout)
            current_price = close_prices[-1]
            breakout_level = right_high

            return {
                'pattern': 'cup_and_handle',
                'confidence': 0.75,
                'cup_bottom': bottom_price,
                'breakout_level': breakout_level,
                'current_price': current_price,
                'potential_target': breakout_level * 1.20,  # Traditional target is cup depth added to breakout
                'near_breakout': current_price >= breakout_level * 0.98
            }

        except Exception as e:
            logger.error(f"Error detecting cup and handle: {str(e)}")
            return None

    @staticmethod
    def detect_consolidation_breakout(price_df: pd.DataFrame, window: int = 30) -> Optional[Dict]:
        """
        Detect consolidation followed by breakout

        Returns:
            Dict with pattern details if found, None otherwise
        """
        try:
            if len(price_df) < window + 5:
                return None

            # Look at consolidation period
            consolidation_df = price_df.iloc[-window-5:-5]
            recent_df = price_df.tail(5)

            # Calculate price range during consolidation
            consolidation_high = consolidation_df['high'].max()
            consolidation_low = consolidation_df['low'].min()
            consolidation_range = consolidation_high - consolidation_low
            avg_price = consolidation_df['close'].mean()

            # Check if price range is tight (consolidation)
            relative_range = consolidation_range / avg_price

            if relative_range > 0.10:  # More than 10% range is not consolidation
                return None

            # Check for breakout in recent days
            recent_high = recent_df['high'].max()
            recent_volume = recent_df['volume'].mean()
            consolidation_volume = consolidation_df['volume'].mean()

            # Breakout should be on higher volume
            volume_increase = recent_volume / consolidation_volume if consolidation_volume > 0 else 1

            if recent_high > consolidation_high and volume_increase > 1.3:
                return {
                    'pattern': 'consolidation_breakout',
                    'confidence': min(0.80, 0.60 + (volume_increase - 1.3) * 0.2),
                    'consolidation_high': consolidation_high,
                    'consolidation_low': consolidation_low,
                    'breakout_price': recent_high,
                    'volume_increase': volume_increase,
                    'potential_target': consolidation_high + consolidation_range
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting consolidation breakout: {str(e)}")
            return None

    @staticmethod
    def detect_pullback_to_ma(price_df: pd.DataFrame, ma_period: int = 50) -> Optional[Dict]:
        """
        Detect pullback to moving average in an uptrend

        Returns:
            Dict with pattern details if found, None otherwise
        """
        try:
            if len(price_df) < ma_period + 20:
                return None

            df = price_df.copy()

            # Calculate moving average
            df['ma'] = df['close'].rolling(window=ma_period).mean()

            # Check for uptrend (MA sloping up)
            recent_ma = df['ma'].tail(20)
            if recent_ma.iloc[-1] <= recent_ma.iloc[0]:
                return None  # Not in uptrend

            # Check if price recently touched or is near MA
            recent_df = df.tail(10)
            min_distance = ((recent_df['low'] - recent_df['ma']) / recent_df['ma']).min()

            # Price should be within 3% of MA
            if min_distance > 0.03:
                return None

            # Current price should be bouncing off MA
            current_price = df['close'].iloc[-1]
            current_ma = df['ma'].iloc[-1]

            if current_price > current_ma * 0.98:  # Within 2% of MA or above
                return {
                    'pattern': 'pullback_to_ma',
                    'confidence': 0.70,
                    'ma_period': ma_period,
                    'ma_value': current_ma,
                    'current_price': current_price,
                    'support_level': current_ma,
                    'potential_target': current_ma * 1.10
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting pullback to MA: {str(e)}")
            return None

    @staticmethod
    def detect_volume_surge(price_df: pd.DataFrame, threshold: float = 2.0) -> Optional[Dict]:
        """
        Detect unusual volume surge

        Args:
            threshold: Volume must be this multiple of average (default 2.0x)

        Returns:
            Dict with pattern details if found, None otherwise
        """
        try:
            if len(price_df) < 30:
                return None

            df = price_df.copy()

            # Calculate average volume (excluding today)
            avg_volume = df['volume'].iloc[:-1].tail(20).mean()
            current_volume = df['volume'].iloc[-1]

            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            if volume_ratio >= threshold:
                # Check if price is moving up with volume
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]

                return {
                    'pattern': 'volume_surge',
                    'confidence': min(0.85, 0.60 + (volume_ratio - threshold) * 0.1),
                    'volume_ratio': volume_ratio,
                    'avg_volume': avg_volume,
                    'current_volume': current_volume,
                    'price_change_percent': price_change * 100,
                    'bullish_volume': price_change > 0
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting volume surge: {str(e)}")
            return None

    @staticmethod
    def find_all_patterns(price_df: pd.DataFrame) -> List[Dict]:
        """
        Run all pattern detection methods and return all found patterns

        Returns:
            List of pattern dictionaries
        """
        patterns = []

        # Try each pattern detection method
        cup_handle = PatternMatcher.detect_cup_and_handle(price_df)
        if cup_handle:
            patterns.append(cup_handle)

        consolidation = PatternMatcher.detect_consolidation_breakout(price_df)
        if consolidation:
            patterns.append(consolidation)

        pullback = PatternMatcher.detect_pullback_to_ma(price_df)
        if pullback:
            patterns.append(pullback)

        volume = PatternMatcher.detect_volume_surge(price_df)
        if volume:
            patterns.append(volume)

        return patterns

    @staticmethod
    def compare_to_historical(current_pattern: np.ndarray,
                            historical_patterns: List[np.ndarray],
                            threshold: float = 0.15) -> List[Tuple[int, float]]:
        """
        Compare current price pattern to historical patterns using DTW

        Args:
            current_pattern: Normalized current price pattern
            historical_patterns: List of normalized historical patterns
            threshold: Similarity threshold (lower = more similar)

        Returns:
            List of (index, distance) tuples for similar patterns
        """
        similar_patterns = []

        try:
            for idx, hist_pattern in enumerate(historical_patterns):
                # Use Dynamic Time Warping for pattern matching
                distance, _ = fastdtw(current_pattern.reshape(-1, 1),
                                     hist_pattern.reshape(-1, 1),
                                     dist=euclidean)

                # Normalize distance by pattern length
                normalized_distance = distance / len(current_pattern)

                if normalized_distance <= threshold:
                    similar_patterns.append((idx, normalized_distance))

            # Sort by similarity (lower distance = more similar)
            similar_patterns.sort(key=lambda x: x[1])

            return similar_patterns

        except Exception as e:
            logger.error(f"Error comparing to historical patterns: {str(e)}")
            return []
