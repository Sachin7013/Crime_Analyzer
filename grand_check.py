#!/usr/bin/env python3
"""
AlgoOrange Grant Eligibility Analyzer
Analyzes Australian business grants for eligibility using Claude AI
"""

import json
import os
from anthropic import Anthropic
from datetime import datetime
from typing import Optional, List, Dict
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed...")

# ✅ GET API KEY FROM .env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ✅ CHECK IF IT EXISTS
if not ANTHROPIC_API_KEY:
    print("❌ ERROR: ANTHROPIC_API_KEY not found!")
    exit(1)

# ✅ PASS TO CLIENT
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ============================================================================
# ALGORANGE ORGANIZATION PROFILE
# ============================================================================

ORGANIZATION_INFO = {
    "name": "AlgoOrange",
    "tagline": "AI-Powered Vision Intelligence, Automation & Enterprise Software Solutions",
    
    "industry": [
        "Artificial Intelligence",
        "Computer Vision",
        "Industrial Automation",
        "Workflow Automation",
        "Enterprise Software Development"
    ],

    "location": "Sydney, Australia",
    "country": "Australia",

    "business_type": (
        "AI-Powered Software Development and Intelligent Automation Company "
        "specializing in Vision AI, IoT Integration, Workflow Automation, "
        "Compliance Platforms, and Custom Enterprise Software Solutions."
    ),

    "company_overview": (
        "AlgoOrange is a technology company focused on building scalable, "
        "production-ready AI and automation solutions for enterprises, "
        "government organizations, educational institutions, industrial facilities, "
        "and commercial operations. We specialize in computer vision systems, "
        "intelligent monitoring platforms, workflow automation engines, compliance "
        "management solutions, and custom AI-powered applications."
    ),

    "team": {
        "size": 3,
        "profile": (
            "A highly specialized team of software engineers with expertise in "
            "Artificial Intelligence, Computer Vision, Large Language Models (LLMs), "
            "Cloud Architecture, Enterprise Software Development, and System Integration."
        ),
        "experience": (
            "Hands-on experience designing, developing, and deploying AI-powered "
            "solutions across computer vision, workflow automation, compliance "
            "management, and intelligent monitoring domains."
        )
    },

    "technology_expertise": [
        "Computer Vision",
        "Vision Language Models (VLMs)",
        "Large Language Models (LLMs)",
        "Multi-Agent AI Systems",
        "Real-Time Object Detection",
        "Object Tracking & Analytics",
        "Natural Language Query Systems",
        "Semantic Search",
        "Knowledge Retrieval Systems",
        "Workflow Automation Engines",
        "IoT Device Integration",
        "Cloud-Native Applications",
        "API Development & Integration",
        "Data Analytics & Reporting",
        "Event-Driven Architectures"
    ],

    "technology_stack": [
        "Python",
        "FastAPI",
        "YOLO",
        "Gemini AI",
        "OpenAI Models",
        "AWS",
        "MongoDB",
        "PostgreSQL",
        "Docker",
        "REST APIs",
        "Vector Databases",
        "IoT Protocols",
        "Real-Time Streaming Systems"
    ],

    "core_capabilities": [
        {
            "service": "Vision AI & Intelligent Monitoring Solutions",
            "description": (
                "Development of configurable computer vision platforms capable of "
                "integrating with CCTV cameras, IP cameras, drones, and video streams "
                "for real-time monitoring, detection, analytics, and alerting."
            ),
            "use_cases": [
                "PPE Compliance Monitoring",
                "Worker Safety Monitoring",
                "Intrusion Detection",
                "Fire & Smoke Detection",
                "Crowd Monitoring",
                "Vehicle Detection & Tracking",
                "Traffic Analytics",
                "Warehouse Operations Monitoring",
                "Student Safety Monitoring",
                "Attendance & Occupancy Analytics"
            ]
        },
        {
            "service": "IoT AI & Industrial Automation Solutions",
            "description": (
                "Integration of AI systems with industrial sensors, PLCs, telemetry "
                "devices, and operational systems to enable real-time monitoring, "
                "predictive insights, and automated response workflows."
            ),
            "use_cases": [
                "Predictive Maintenance",
                "Industrial Safety Monitoring",
                "Equipment Health Monitoring",
                "Environmental Monitoring",
                "Smart Factory Automation",
                "Energy Consumption Optimization"
            ]
        },
        {
            "service": "Compliance & Workflow Automation Platforms",
            "description": (
                "Development of configurable approval workflows, governance systems, "
                "audit management platforms, compliance tracking solutions, and "
                "business process automation tools."
            ),
            "use_cases": [
                "Multi-Level Approval Workflows",
                "Leave Management Systems",
                "Procurement Approval Systems",
                "Incident Management Platforms",
                "Audit & Compliance Tracking",
                "Risk Assessment Workflows",
                "Evidence Management Systems",
                "Corrective Action Management"
            ]
        },
        {
            "service": "Custom AI-Powered Software Development",
            "description": (
                "Rapid development of enterprise-grade web applications, SaaS products, "
                "AI assistants, operational dashboards, customer portals, and "
                "industry-specific software solutions."
            ),
            "use_cases": [
                "Enterprise Applications",
                "SaaS Platforms",
                "AI Copilots",
                "Agentic AI Systems",
                "Document Intelligence Solutions",
                "Knowledge Management Systems",
                "Analytics Platforms",
                "Business Automation Systems"
            ]
        }
    ],

    "target_industries": [
        "Manufacturing",
        "Industrial Facilities",
        "Mining",
        "Construction",
        "Warehousing & Logistics",
        "Transportation",
        "Retail",
        "Educational Institutions",
        "Smart Cities",
        "Government Organizations",
        "Public Infrastructure",
        "Healthcare Facilities",
        "Commercial Buildings"
    ],

    "competitive_advantages": [
        "Rapid AI Solution Development",
        "Specification-Driven Engineering",
        "Configurable Vision AI Platform",
        "Environment-Agnostic Deployment",
        "Camera-Agnostic Architecture",
        "Cloud and On-Premise Deployment Support",
        "Custom Workflow Engine Development",
        "End-to-End Product Ownership",
        "Enterprise System Integration Expertise"
    ],

    "deployment_models": [
        "Cloud",
        "On-Premise",
        "Hybrid"
    ],

    "business_registration": {
        "india_registered": False,
        "australia_registered": False,
        "australia_tax_registered": False,
        "gst_registered": False,
        "australian_bank_account": False
    },

    "previous_grants": [],
    "government_contracts": [],
    "certifications": [],

    "future_focus": [
        "Industrial AI",
        "Autonomous Monitoring Systems",
        "Vision-Language AI",
        "Smart Infrastructure",
        "Compliance Automation",
        "Enterprise AI Agents"
    ]
}


# ============================================================================
# SYSTEM PROMPT FOR CLAUDE
# ============================================================================

def create_system_prompt() -> str:
    """
    Create the system prompt that guides Claude's analysis.
    """
    
    # Format organization info nicely
    org_profile = f"""
ORGANIZATION: {ORGANIZATION_INFO['name']}
Tagline: {ORGANIZATION_INFO['tagline']}

LOCATION: {ORGANIZATION_INFO['location']} (Based in {ORGANIZATION_INFO['country']})

BUSINESS TYPE:
{ORGANIZATION_INFO['business_type']}

COMPANY OVERVIEW:
{ORGANIZATION_INFO['company_overview']}

TEAM:
- Size: {ORGANIZATION_INFO['team']['size']} specialized engineers
- Profile: {ORGANIZATION_INFO['team']['profile']}
- Experience: {ORGANIZATION_INFO['team']['experience']}

CORE TECHNOLOGIES:
{chr(10).join(f"• {tech}" for tech in ORGANIZATION_INFO['technology_expertise'])}

TECHNOLOGY STACK:
{chr(10).join(f"• {tech}" for tech in ORGANIZATION_INFO['technology_stack'])}

CORE SERVICE AREAS:
"""
    
    for service in ORGANIZATION_INFO['core_capabilities']:
        org_profile += f"\n• {service['service']}"
        org_profile += f"\n  {service['description']}"
        org_profile += f"\n  Use cases: {', '.join(service['use_cases'][:3])}..."
    
    org_profile += f"\n\nTARGET INDUSTRIES:"
    org_profile += f"\n{', '.join(ORGANIZATION_INFO['target_industries'])}"
    
    org_profile += f"\n\nCOMPETITIVE ADVANTAGES:"
    org_profile += f"\n{chr(10).join(f'• {adv}' for adv in ORGANIZATION_INFO['competitive_advantages'])}"
    
    org_profile += f"\n\nDEPLOYMENT MODELS: {', '.join(ORGANIZATION_INFO['deployment_models'])}"
    
    org_profile += f"\n\nAUSTRALIAN REGISTRATION STATUS:"
    org_profile += f"\n• Registered in Australia: {ORGANIZATION_INFO['business_registration']['australia_registered']}"
    org_profile += f"\n• Tax Registered in Australia: {ORGANIZATION_INFO['business_registration']['australia_tax_registered']}"
    org_profile += f"\n• GST Registered: {ORGANIZATION_INFO['business_registration']['gst_registered']}"
    org_profile += f"\n• Australian Bank Account: {ORGANIZATION_INFO['business_registration']['australian_bank_account']}"
    
    analysis_instructions = """
CRITICAL CONSIDERATIONS FOR THIS ORGANIZATION:
1. ⚠️ This is an India-based company, NOT an Australian company
2. ⚠️ Most Australian government grants prioritize Australian-registered entities
3. ⚠️ International companies may be excluded or face significant barriers
4. ⚠️ Check citizenship, residency, tax registration requirements carefully
5. ⚠️ Look for grants that support international AI/tech companies or research partnerships
6. ⚠️ Some grants may allow applications if company establishes Australian operations

ANALYSIS REQUIREMENTS:
For each grant, provide structured analysis with these sections:

1. **ELIGIBILITY SCORE** (0-100%):
   - 90-100%: Highly applicable - Can apply with confidence
   - 70-89%: Good fit - Meet key criteria, minor gaps
   - 50-69%: Moderate - Meet some criteria, significant gaps exist
   - 30-49%: Low applicability - Major barriers exist
   - 0-29%: Not eligible - Fundamental blockers

2. **DETAILED ANALYSIS**:
   {
     "grant_title": "...",
     "applicability_score": XX,
     "recommendation": "STRONG CANDIDATE | WORTH PURSUING | NEEDS INVESTIGATION | NOT ELIGIBLE",
     "key_matches": ["What aligns with AlgoOrange"],
     "key_mismatches": ["What doesn't align"],
     "critical_blockers": ["Deal-breakers if any"],
     "geographic_fit": "...",
     "industry_relevance": "...",
     "technology_alignment": "...",
     "team_experience_match": "...",
     "registration_requirements": "...",
     "international_company_eligible": "Yes/No/Maybe",
     "workarounds_or_pathways": ["Possible solutions"],
     "questions_to_ask_provider": ["Ask these questions"],
     "action_items": ["What to do next"],
     "reasoning": "Why this score and recommendation"
   }

3. **RECOMMENDATION LOGIC**:
   - STRONG CANDIDATE: Apply immediately, high success probability
   - WORTH PURSUING: Check details further, clarify with provider
   - NEEDS INVESTIGATION: Unclear if eligible, needs more research
   - NOT ELIGIBLE: Don't apply, significant barriers exist

Be honest and conservative. If international companies are not eligible, say so clearly.
If there are workarounds (like establishing Australian operations), mention them.
Always prioritize accuracy over optimism."""

    return (
        "You are an expert Australian business grants analyst specializing in grants from business.gov.au.\n\n"
        "Your task is to analyze grants for eligibility and provide detailed recommendations for the following organization:\n\n"
        + org_profile
        + analysis_instructions
    )


# ============================================================================
# GRANT ANALYSIS FUNCTIONS
# ============================================================================

def analyze_grant_eligibility(grant_data: Dict, conversation_history: List) -> Dict:
    """
    Analyze a single grant's eligibility using Claude AI.
    
    Args:
        grant_data: Grant information from JSON
        conversation_history: Previous conversation messages
    
    Returns:
        Analysis result with eligibility score and reasoning
    """
    
    grant_text = f"""
GRANT TO ANALYZE FOR ALGORANGE:

Title: {grant_data.get('title', 'N/A')}
Status: {grant_data.get('status', 'Unknown')}
URL: {grant_data.get('url', 'N/A')}
Close Date: {grant_data.get('closeDate', 'N/A')}

GRANT DETAILS:
Overview:
{grant_data.get('overview', 'N/A')}

Who is this for:
{grant_data.get('who_is_this_for', 'N/A')}

What do you get:
{grant_data.get('what_do_you_get', 'N/A')}

How to apply:
{grant_data.get('how_to_apply', 'N/A')}

Eligibility criteria:
{grant_data.get('check_if_you_can_apply', 'N/A')}

---

Please provide a detailed eligibility analysis for AlgoOrange (India-based AI/Computer Vision company).
Focus on:
1. Whether international companies can apply
2. Any geographic or location restrictions
3. Any citizenship/residency requirements
4. Technology/industry alignment
5. Possible barriers and workarounds
"""
    
    conversation_history.append({
        "role": "user",
        "content": grant_text
    })
    
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2500,
            system=create_system_prompt(),
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return {
            "analysis": assistant_message,
            "grant_title": grant_data.get('title'),
            "grant_url": grant_data.get('url'),
            "status": grant_data.get('status'),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": f"Error analyzing grant: {str(e)}",
            "grant_title": grant_data.get('title'),
            "success": False
        }


def ask_followup_question(question: str, conversation_history: List) -> str:
    """
    Ask a follow-up question about the current grant analysis.
    
    Args:
        question: The follow-up question
        conversation_history: Previous conversation messages
    
    Returns:
        Assistant's response
    """
    
    conversation_history.append({
        "role": "user",
        "content": question
    })
    
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            system=create_system_prompt(),
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
        
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_grants_file(input_file: str, output_file: str, limit: Optional[int] = None):
    """
    Process all grants from JSON file and analyze eligibility.
    """
    
    print(f"\n📂 Loading grants from: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            grants = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        return
    
    print(f"📊 Found {len(grants)} total grants")
    
    # Filter open grants
    open_grants = [g for g in grants if g.get('status') == 'Open']
    print(f"🟢 {len(open_grants)} open grants available")
    
    if limit:
        open_grants = open_grants[:limit]
        print(f"🔄 Analyzing first {limit} grants\n")
    else:
        print(f"🔄 Analyzing all {len(open_grants)} grants\n")
    
    results = []
    conversation_history = []
    
    for index, grant in enumerate(open_grants, 1):
        
        print(f"[{index}/{len(open_grants)}] 🔍 {grant.get('title', 'Unknown')[:70]}...")
        
        analysis = analyze_grant_eligibility(grant, conversation_history)
        
        results.append({
            "grant": {
                "id": grant.get('id'),
                "title": grant.get('title'),
                "url": grant.get('url'),
                "status": grant.get('status'),
                "closeDate": grant.get('closeDate')
            },
            "analysis": analysis.get('analysis'),
            "error": analysis.get('error'),
            "analyzed_at": datetime.now().isoformat()
        })
        
        if analysis.get('success'):
            print(f"    ✅ Complete\n")
        else:
            print(f"    ⚠️  Error\n")
    
    # Save results
    print(f"\n💾 Saving results to: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analyzed {len(results)} grants")
        print(f"📊 Results saved successfully")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode(input_file: str):
    """
    Interactive mode for analyzing grants one by one.
    """
    
    print(f"\n📂 Loading grants...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            grants = json.load(f)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # Filter open grants
    open_grants = [g for g in grants if g.get('status') == 'Open']
    print(f"🟢 Loaded {len(open_grants)} open grants\n")
    
    conversation_history = []
    current_index = 0
    
    while current_index < len(open_grants):
        
        grant = open_grants[current_index]
        
        print(f"\n{'='*80}")
        print(f"GRANT {current_index + 1}/{len(open_grants)}")
        print(f"{'='*80}")
        print(f"Title: {grant.get('title')}")
        print(f"Status: {grant.get('status')}")
        print(f"URL: {grant.get('url')}\n")
        
        print("🔍 Analyzing eligibility...\n")
        analysis = analyze_grant_eligibility(grant, conversation_history)
        
        print("ANALYSIS:")
        print("-" * 80)
        print(analysis.get('analysis', analysis.get('error')))
        print("-" * 80)
        
        # Interactive menu
        while True:
            print(f"\n[n] Next | [q] Ask Question | [s] Save & Exit | [c] Clear History | [skip] Skip")
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 'n':
                current_index += 1
                break
            
            elif choice == 'q':
                follow_up = input("\n❓ Your question: ").strip()
                if follow_up:
                    print("\n⏳ Getting response...\n")
                    response = ask_followup_question(follow_up, conversation_history)
                    print(response)
            
            elif choice == 's':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"grant_analysis_{current_index + 1}_{timestamp}.json"
                print(f"\n💾 Saving conversation...")
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "grant": {
                                "title": grant.get('title'),
                                "url": grant.get('url')
                            },
                            "conversation": conversation_history,
                            "saved_at": timestamp
                        }, f, indent=2)
                    print(f"✅ Saved to {output_file}")
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                return
            
            elif choice == 'c':
                conversation_history = []
                print("\n🔄 Conversation history cleared")
                break
            
            elif choice == 'skip':
                current_index += 1
                break
            
            else:
                print("❌ Invalid choice. Try again.")
    
    print("\n✅ All grants reviewed!")


# ============================================================================
# MAIN MENU
# ============================================================================

def show_header():
    """Display application header."""
    print("\n" + "="*80)
    print("🎯 ALGORANGE - AUSTRALIAN GRANT ELIGIBILITY ANALYZER")
    print("="*80)
    print(f"\nOrganization: {ORGANIZATION_INFO['name']}")
    print(f"Location: {ORGANIZATION_INFO['location']}")
    print(f"Focus: {', '.join(ORGANIZATION_INFO['industry'][:3])}...")
    print(f"Team Size: {ORGANIZATION_INFO['team']['size']} engineers")


def main():
    """Main entry point."""
    
    show_header()
    
    # File path
    input_file = r"C:\Users\Manoj\OneDrive\Desktop\fall_detection\web_crawling\output.json"
    
    if not os.path.exists(input_file):
        print(f"\n❌ Error: File not found at:")
        print(f"   {input_file}")
        print(f"\n📝 Please update the file path in the code or place your grants JSON there.")
        return
    
    print("\n" + "="*80)
    print("CHOOSE ANALYSIS MODE:")
    print("="*80)
    print("[1] Interactive Mode - Analyze one by one with follow-up questions")
    print("    👉 Best for detailed analysis and understanding each grant")
    print()
    print("[2] Batch Mode (All) - Analyze all grants at once")
    print("    👉 Best for quick overview of all grants")
    print()
    print("[3] Batch Mode (Limited) - Analyze first N grants")
    print("    👉 Best for testing with smaller sample")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        interactive_mode(input_file)
    
    elif choice == '2':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"algorange_grants_analysis_all_{timestamp}.json"
        process_grants_file(input_file, output_file)
        print(f"\n📊 Results saved to: {output_file}")
    
    elif choice == '3':
        try:
            limit = int(input("\nHow many grants to analyze? ").strip())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"algorange_grants_analysis_{limit}_{timestamp}.json"
            process_grants_file(input_file, output_file, limit=limit)
            print(f"\n📊 Results saved to: {output_file}")
        except ValueError:
            print("❌ Invalid number. Please enter a valid integer.")
    
    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()