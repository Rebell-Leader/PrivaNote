import json
import os
from openai import OpenAI
import streamlit as st
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class AIAnalysisService:
    """Handle AI-powered analysis of meeting transcripts with dual-mode support"""
    
    def __init__(self, provider='openai', model_name=None, lm_studio_config=None):
        self.provider = provider
        self.model_name = model_name or self._get_default_model()
        self.lm_studio_config = lm_studio_config or {'host': 'localhost', 'port': 1234}
        self.openai_client = self._initialize_openai_client()
        self.ollama_available = self._check_ollama_availability()
        self.lm_studio_client = self._initialize_lm_studio_client()
        self.lm_studio_available = self._check_lm_studio_availability()
        
    def _get_default_model(self):
        """Get default model for the selected provider"""
        if self.provider == 'ollama':
            return 'gemma3'
        elif self.provider == 'lm_studio':
            return 'google/gemma-3n-e4b'
        return 'gpt-4o'
        
    def _check_ollama_availability(self):
        """Check if Ollama is available and running"""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            # Test Ollama connection
            ollama.list()
            return True
        except Exception:
            return False
    
    def _initialize_openai_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)
        
    def _initialize_lm_studio_client(self):
        """Initialize LM Studio client (OpenAI-compatible)"""
        try:
            host = self.lm_studio_config.get('host', 'localhost')
            port = self.lm_studio_config.get('port', 1234)
            base_url = f"http://{host}:{port}/v1"
            
            # LM Studio uses OpenAI-compatible API - use "lm-studio" as API key
            client = OpenAI(
                api_key="lm-studio",
                base_url=base_url,
                timeout=10.0  # Add timeout for better error handling
            )
            return client
        except Exception as e:
            st.error(f"Failed to initialize LM Studio client: {str(e)}")
            return None
            
    def _check_lm_studio_availability(self):
        """Check if LM Studio is available and running"""
        if not self.lm_studio_client:
            return False
        try:
            # First try to get available models to check connection
            models_response = self.lm_studio_client.models.list()
            
            # If no models are loaded, return False
            if not models_response.data:
                return False
                
            # Check if our configured model is available
            available_models = [model.id for model in models_response.data]
            if self.model_name not in available_models:
                # Try to use the first available model if configured model not found
                if available_models:
                    st.warning(f"Configured model '{self.model_name}' not found. Available models: {', '.join(available_models)}")
                    return True
                return False
                
            return True
        except Exception as e:
            # Log the specific error for debugging
            st.error(f"LM Studio connection test failed: {str(e)}")
            return False
        
    def set_provider(self, provider, model_name=None, lm_studio_config=None):
        """Switch between OpenAI, Ollama, and LM Studio providers"""
        self.provider = provider
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = self._get_default_model()
            
        if lm_studio_config:
            self.lm_studio_config = lm_studio_config
            self.lm_studio_client = self._initialize_lm_studio_client()
            self.lm_studio_available = self._check_lm_studio_availability()
            
    def get_available_providers(self):
        """Get list of available AI providers"""
        providers = []
        
        if self.openai_client:
            providers.append({
                'name': 'OpenAI (Cloud)',
                'value': 'openai',
                'description': 'High-quality analysis via OpenAI API',
                'privacy': 'Transcript sent to OpenAI',
                'models': ['gpt-4o', 'gpt-4o-mini']
            })
            
        if self.ollama_available:
            try:
                # Get available Ollama models
                models_response = ollama.list()
                available_models = [model['name'] for model in models_response.get('models', [])]
                providers.append({
                    'name': 'Local Gemma (Ollama)',
                    'value': 'ollama', 
                    'description': 'Fully private local processing',
                    'privacy': 'Data never leaves your device',
                    'models': available_models if available_models else ['gemma3']
                })
            except Exception:
                pass
                
        if self.lm_studio_available:
            try:
                # Get available LM Studio models
                models_response = self.lm_studio_client.models.list()
                available_models = [model.id for model in models_response.data]
                host = self.lm_studio_config.get('host', 'localhost')
                port = self.lm_studio_config.get('port', 1234)
                providers.append({
                    'name': f'LM Studio ({host}:{port})',
                    'value': 'lm_studio',
                    'description': 'Local server with OpenAI-compatible API',
                    'privacy': 'Data processed on local LM Studio server',
                    'models': available_models if available_models else ['No models loaded']
                })
            except Exception as e:
                # Still add the provider but indicate connection issues
                host = self.lm_studio_config.get('host', 'localhost')
                port = self.lm_studio_config.get('port', 1234)
                providers.append({
                    'name': f'LM Studio ({host}:{port}) - Connection Failed',
                    'value': 'lm_studio',
                    'description': 'Local server with OpenAI-compatible API',
                    'privacy': 'Data processed on local LM Studio server',
                    'models': [f'Connection error: {str(e)}']
                })
                
        if not providers:
            providers.append({
                'name': 'Basic Analysis (No AI)',
                'value': 'fallback',
                'description': 'Simple keyword-based analysis',
                'privacy': 'Fully local',
                'models': ['pattern-matching']
            })
            
        return providers
    
    def analyze_meeting(self, transcript):
        """
        Perform comprehensive AI analysis of meeting transcript
        
        Args:
            transcript (str): Meeting transcript text
            
        Returns:
            dict: Analysis results including summary, action items, and key decisions
        """
        if self.provider == 'openai' and self.openai_client:
            return self._analyze_with_openai(transcript)
        elif self.provider == 'ollama' and self.ollama_available:
            return self._analyze_with_ollama(transcript)
        elif self.provider == 'lm_studio' and self.lm_studio_available:
            return self._analyze_with_lm_studio(transcript)
        else:
            return self._fallback_analysis(transcript)
            
    def _analyze_with_openai(self, transcript):
        """Analyze using OpenAI API"""
        try:
            analysis_result = self._generate_openai_analysis(transcript)
            return {
                'summary': analysis_result.get('summary', ''),
                'action_items': analysis_result.get('action_items', []),
                'key_decisions': analysis_result.get('key_decisions', []),
                'topics_discussed': analysis_result.get('topics_discussed', []),
                'participants': analysis_result.get('participants', []),
                'next_steps': analysis_result.get('next_steps', []),
                'ai_confidence': analysis_result.get('confidence', 0.85),
                'provider': 'OpenAI'
            }
        except Exception as e:
            st.error(f"OpenAI analysis failed: {str(e)}")
            return self._fallback_analysis(transcript)
            
    def _analyze_with_ollama(self, transcript):
        """Analyze using local Ollama/Gemma"""
        try:
            analysis_result = self._generate_ollama_analysis(transcript)
            return {
                'summary': analysis_result.get('summary', ''),
                'action_items': analysis_result.get('action_items', []),
                'key_decisions': analysis_result.get('key_decisions', []),
                'topics_discussed': analysis_result.get('topics_discussed', []),
                'participants': analysis_result.get('participants', []),
                'next_steps': analysis_result.get('next_steps', []),
                'ai_confidence': analysis_result.get('confidence', 0.75),
                'provider': f'Local {self.model_name}'
            }
        except Exception as e:
            st.error(f"Local AI analysis failed: {str(e)}")
            return self._fallback_analysis(transcript)
            
    def _analyze_with_lm_studio(self, transcript):
        """Analyze using LM Studio (OpenAI-compatible API)"""
        try:
            analysis_result = self._generate_lm_studio_analysis(transcript)
            return {
                'summary': analysis_result.get('summary', ''),
                'action_items': analysis_result.get('action_items', []),
                'key_decisions': analysis_result.get('key_decisions', []),
                'topics_discussed': analysis_result.get('topics_discussed', []),
                'participants': analysis_result.get('participants', []),
                'next_steps': analysis_result.get('next_steps', []),
                'ai_confidence': analysis_result.get('confidence', 0.8),
                'provider': f'LM Studio ({self.model_name})'
            }
        except Exception as e:
            st.error(f"LM Studio analysis failed: {str(e)}")
            return self._fallback_analysis(transcript)
    
    def _generate_ollama_analysis(self, transcript):
        """Generate comprehensive meeting analysis using local Ollama/Gemma"""
        
        system_prompt = """You are an expert meeting analyst. Analyze the provided meeting transcript and extract key information in a structured JSON format. Focus on being accurate and concise.

Your analysis should include:
1. A clear, concise summary of the meeting
2. Specific action items with clear ownership when mentioned
3. Key decisions that were made
4. Main topics discussed
5. Identified participants (if names are mentioned)
6. Next steps or follow-up items

Be precise and only include information that is clearly stated or strongly implied in the transcript. Respond only with valid JSON."""

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
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                options={
                    'temperature': 0.3,
                    'num_predict': 1000
                }
            )
            
            content = response['message']['content']
            if content:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
                # If no JSON found, try parsing the whole response
                return json.loads(content)
            return {}
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse local AI response: {str(e)}")
            return self._fallback_analysis(transcript)
        except Exception as e:
            st.error(f"Local AI error: {str(e)}")
            return self._fallback_analysis(transcript)
            
    def _generate_openai_analysis(self, transcript):
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
            if not self.openai_client:
                return self._fallback_analysis(transcript)
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
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
    
    def _generate_lm_studio_analysis(self, transcript):
        """Generate comprehensive meeting analysis using LM Studio"""
        
        system_prompt = """You are an expert meeting analyst. Analyze the provided meeting transcript and extract key information in a structured JSON format. Focus on being accurate and concise.

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
            if not self.lm_studio_client:
                return self._fallback_analysis(transcript)
            
            # Get available models to use the correct model name
            try:
                models_response = self.lm_studio_client.models.list()
                available_models = [model.id for model in models_response.data]
                
                # Use configured model if available, otherwise use first available
                model_to_use = self.model_name
                if self.model_name not in available_models and available_models:
                    model_to_use = available_models[0]
                    st.info(f"Using model '{model_to_use}' instead of configured '{self.model_name}'")
                    
            except Exception:
                # If we can't get models list, try with configured model anyway
                model_to_use = self.model_name
            
            response = self.lm_studio_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            if content:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
                # If no JSON found, try parsing the whole response
                return json.loads(content)
            return {}
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse LM Studio response: {str(e)}")
            return self._fallback_analysis(transcript)
        except Exception as e:
            st.error(f"LM Studio API error: {str(e)}")
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
        if not self.openai_client:
            return self._simple_summary(transcript, max_length)
        
        try:
            prompt = f"""Summarize this meeting transcript in {max_length} words or less. Focus on the main points, decisions, and outcomes:

{transcript}"""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
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
        if not self.openai_client:
            return self._simple_action_extraction(transcript)
        
        try:
            prompt = f"""Extract specific action items from this meeting transcript. Look for tasks, assignments, commitments, and follow-up items. Format as a JSON array of strings:

{transcript}

Respond with only a JSON array of action items."""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
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
        return self.openai_client is not None
