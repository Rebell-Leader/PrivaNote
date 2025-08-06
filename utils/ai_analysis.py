import json
import os
from openai import OpenAI
import streamlit as st

class AIAnalysisService:
    """Handle AI-powered analysis of meeting transcripts"""
    
    def __init__(self):
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.warning("⚠️ OpenAI API key not found. AI analysis features will be limited.")
            return None
        
        return OpenAI(api_key=api_key)
    
    def analyze_meeting(self, transcript):
        """
        Perform comprehensive AI analysis of meeting transcript
        
        Args:
            transcript (str): Meeting transcript text
            
        Returns:
            dict: Analysis results including summary, action items, and key decisions
        """
        if not self.client:
            return self._fallback_analysis(transcript)
        
        try:
            # Generate comprehensive analysis
            analysis_result = self._generate_comprehensive_analysis(transcript)
            
            return {
                'summary': analysis_result.get('summary', ''),
                'action_items': analysis_result.get('action_items', []),
                'key_decisions': analysis_result.get('key_decisions', []),
                'topics_discussed': analysis_result.get('topics_discussed', []),
                'participants': analysis_result.get('participants', []),
                'next_steps': analysis_result.get('next_steps', []),
                'ai_confidence': analysis_result.get('confidence', 0.8)
            }
            
        except Exception as e:
            st.error(f"AI analysis failed: {str(e)}")
            return self._fallback_analysis(transcript)
    
    def _generate_comprehensive_analysis(self, transcript):
        """Generate comprehensive meeting analysis using OpenAI"""
        
        system_prompt = """You are an expert meeting analyst. Analyze the provided meeting transcript and extract key information in a structured format. Focus on being accurate and concise.

Your analysis should include:
1. A clear, concise summary of the meeting
2. Specific action items with clear ownership when mentioned
3. Key decisions that were made
4. Main topics discussed
5. Identified participants (if names are mentioned)
6. Next steps or follow-up items

Be precise and only include information that is clearly stated or strongly implied in the transcript. If something is unclear, don't make assumptions."""

        user_prompt = f"""Please analyze this meeting transcript and provide a comprehensive analysis:

TRANSCRIPT:
{transcript}

Respond with a JSON object containing:
- summary: A concise 2-3 sentence summary of the meeting
- action_items: Array of specific action items (what needs to be done)
- key_decisions: Array of important decisions that were made
- topics_discussed: Array of main topics/subjects discussed
- participants: Array of participant names mentioned in the transcript
- next_steps: Array of follow-up actions or next meeting items
- confidence: A number between 0 and 1 indicating your confidence in the analysis"""

        try:
            if not self.client:
                return self._fallback_analysis(transcript)
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result
            return {}
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {str(e)}")
            return self._fallback_analysis(transcript)
        except Exception as e:
            st.error(f"OpenAI API error: {str(e)}")
            return self._fallback_analysis(transcript)
    
    def generate_summary(self, transcript, max_length=200):
        """
        Generate a focused summary of the meeting
        
        Args:
            transcript (str): Meeting transcript
            max_length (int): Maximum summary length in words
            
        Returns:
            str: Meeting summary
        """
        if not self.client:
            return self._simple_summary(transcript, max_length)
        
        try:
            prompt = f"""Summarize this meeting transcript in {max_length} words or less. Focus on the main points, decisions, and outcomes:

{transcript}"""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else ""
            
        except Exception as e:
            st.error(f"Summary generation failed: {str(e)}")
            return self._simple_summary(transcript, max_length)
    
    def extract_action_items(self, transcript):
        """
        Extract specific action items from transcript
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            list: List of action items
        """
        if not self.client:
            return self._simple_action_extraction(transcript)
        
        try:
            prompt = f"""Extract specific action items from this meeting transcript. Look for tasks, assignments, commitments, and follow-up items. Format as a JSON array of strings:

{transcript}

Respond with only a JSON array of action items."""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result.get('action_items', [])
            return []
            
        except Exception as e:
            st.error(f"Action item extraction failed: {str(e)}")
            return self._simple_action_extraction(transcript)
    
    def _fallback_analysis(self, transcript):
        """Provide basic analysis when AI service is unavailable"""
        
        # Simple keyword-based analysis
        words = transcript.lower().split()
        word_count = len(words)
        
        # Basic summary (first and last sentences)
        sentences = transcript.split('.')
        summary = f"Meeting transcript contains {word_count} words. "
        if len(sentences) > 2:
            summary += sentences[0].strip() + ". " + sentences[-2].strip() + "."
        
        # Simple action item detection
        action_keywords = ['todo', 'action', 'task', 'will do', 'should', 'need to', 'follow up']
        action_items = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in action_keywords):
                action_items.append(sentence.strip())
        
        # Simple decision detection
        decision_keywords = ['decided', 'agreed', 'conclusion', 'resolved', 'determined']
        decisions = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in decision_keywords):
                decisions.append(sentence.strip())
        
        return {
            'summary': summary,
            'action_items': action_items[:5],  # Limit to 5 items
            'key_decisions': decisions[:5],
            'topics_discussed': [],
            'participants': [],
            'next_steps': [],
            'ai_confidence': 0.3  # Low confidence for fallback
        }
    
    def _simple_summary(self, transcript, max_length):
        """Generate simple summary without AI"""
        words = transcript.split()
        if len(words) <= max_length:
            return transcript
        
        # Take first portion and try to end at sentence boundary
        summary_words = words[:max_length]
        summary_text = ' '.join(summary_words)
        
        # Try to end at last complete sentence
        last_period = summary_text.rfind('.')
        if last_period > len(summary_text) * 0.7:  # Only if we don't lose too much
            summary_text = summary_text[:last_period + 1]
        
        return summary_text + "..."
    
    def _simple_action_extraction(self, transcript):
        """Extract action items using simple pattern matching"""
        action_patterns = [
            r"need to \w+",
            r"will \w+",
            r"should \w+",
            r"action item",
            r"follow up",
            r"todo",
            r"task"
        ]
        
        import re
        sentences = transcript.split('.')
        action_items = []
        
        for sentence in sentences:
            for pattern in action_patterns:
                if re.search(pattern, sentence.lower()):
                    action_items.append(sentence.strip())
                    break
        
        return action_items[:10]  # Limit results
    
    def is_available(self):
        """Check if AI analysis service is available"""
        return self.client is not None
