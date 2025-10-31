#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add accurate English metadata to all Georgian law files.
This metadata will be used for smart searching in the law database web application.
"""

import os
import codecs

# Complete metadata for all 37 law files based on thorough analysis
LAW_METADATA = {
    "administraciuli.txt": {
        "summary": "This is the Administrative Code that defines administrative violations and penalties in San Andreas, including public order violations, discrimination, hunting/fishing regulations, and medical licensing. It establishes administrative liability systems with mitigating/aggravating circumstances, fine amounts for various violations, and jurisdiction of law enforcement agencies (LSPD, FIB, State Prosecutor). It governs administrative offenses separately from criminal offenses based on severity.",
        "keywords": ["administrative code", "violations", "penalties", "fines", "public order", "law enforcement jurisdiction", "administrative liability", "mitigating circumstances", "aggravating factors", "regulatory compliance"]
    },
    "armiis.txt": {
        "summary": "This law establishes the San Andreas National Guard as a military-public structure with special military status under a General's command, reporting to the Governor as Supreme Commander. The Guard's functions include state military security, anti-terrorist operations, protecting strategic objects, and emergency response. It defines internal structure, member rights/obligations, disciplinary procedures, and prosecutor investigation authority.",
        "keywords": ["national guard", "military", "governor command", "anti-terrorism", "strategic protection", "emergency response", "military operations", "state security", "general", "disciplinary system"]
    },
    "biuros.txt": {
        "summary": "This law governs the Federal Investigation Bureau (FIB) operating in San Andreas under the US Department of Justice. FIB investigates federal crimes including terrorism, corruption, money laundering, and cybercrime. It establishes FIB jurisdiction, coordination with prosecutors and law enforcement, agent rights including immunity provisions for official acts, and reporting requirements. The Attorney General supervises FIB operations within the state.",
        "keywords": ["FBI", "federal investigation", "federal crimes", "terrorism", "corruption", "money laundering", "cybercrime", "agent immunity", "attorney general supervision", "federal jurisdiction"]
    },
    "dokumentebis.txt": {
        "summary": "This law regulates state identification documents including passports, identity cards, military certificates, and business licenses. It covers document types (civil, state, special), licensing procedures for firearms, fishing, hunting, and legal practice with associated fees. The law outlines warrant/order systems (AR, SA, SE, FB, IA, FW, AW, IW) authorizing government actions like raids, arrests, and searches. It defines key legal documents including arrest protocols and power of attorney.",
        "keywords": ["identification documents", "passports", "licenses", "firearms permits", "fishing licenses", "hunting licenses", "attorney licenses", "warrants", "search warrants", "government orders", "arrest protocols"]
    },
    "emskanoni.txt": {
        "summary": "This law establishes the Emergency Medical Services (EMS) system in San Andreas, guaranteeing free medical care availability and quality. It defines EMS responsibilities including rapid emergency response, medical transport, examinations, and medication management. The law protects EMS personnel from arrest/search during duty unless direct threat exists, establishes medical confidentiality, allows EMS investigations, and covers medical expertise types and mental health services.",
        "keywords": ["emergency medical services", "EMS", "medical care", "first aid", "hospital transport", "personnel protection", "medical confidentiality", "drug testing", "psychiatric services", "patient rights"]
    },
    "etikis.txt": {
        "summary": "This Ethics Code governs conduct and appearance of all San Andreas state government employees during official duties. It establishes professional conduct principles including state loyalty, avoiding conflicts of interest, respectful communication, and proper hierarchical relationships. The code specifies appearance standards (no unnaturally colored hair, limited makeup, no jewelry, dress code) and tattoo restrictions on face/head. Violations result in warnings and potential criminal liability.",
        "keywords": ["ethics code", "professional conduct", "appearance standards", "dress code", "government employees", "disciplinary action", "conflict of interest", "loyalty", "hierarchy", "behavioral standards"]
    },
    "iaragis.txt": {
        "summary": "This firearms law regulates acquisition, storage, and carrying of weapons in San Andreas. Only licensed gun shops can legally sell firearms. Citizens must pass examinations for firearms licenses and carry weapons in holsters, unloaded. The law prohibits high-caliber weapons for civilians, requires medical certification before carrying guns, and permits self-defense if direct life threat exists. Off-duty public employees cannot carry high-caliber weapons.",
        "keywords": ["firearms", "weapons", "gun licensing", "ammunition", "carrying weapons", "medical certification", "self-defense", "armed officers", "civilian weapons", "weapon registration"]
    },
    "iaragis shenaxva.txt": {
        "summary": "This law governs weapon storage requirements, safe keeping procedures, and security measures for firearms. It establishes standards for how weapons must be stored, locked, and secured when not in use. The law defines responsibilities of weapon owners to prevent unauthorized access, theft, or misuse of firearms through proper storage protocols.",
        "keywords": ["weapon storage", "firearms safety", "gun safes", "secure storage", "unauthorized access prevention", "theft prevention", "storage requirements", "weapon security", "safe keeping", "owner responsibilities"]
    },
    "imunitetis.txt": {
        "summary": "This law establishes immunity provisions for high-ranking officials including Governor, Lieutenant Governor, Chief of Staff, Chief Justice, Associate Justice, Attorney General, FBI Director, LSPD Chief, and National Guard General. Immunity protects from administrative and criminal liability except when posing direct threat to public safety under intoxication. Immunity requires court order to suspend. Officials and security details cannot be arrested, searched, or detained during official duties.",
        "keywords": ["governmental immunity", "official immunity", "arrest protection", "search immunity", "high office protection", "court order suspension", "security personnel immunity", "government officials", "legal exemptions", "duty protection"]
    },
    "inspeqtorebis.txt": {
        "summary": "This law establishes State Inspectors appointed by the Governor to ensure compliance with state laws and regulations. Inspectors must have clean criminal records and legal expertise. They conduct compliance inspections, investigate complaints about government inefficiency, impose administrative fines for violations, and report findings to the Governor. Governor and officials can suspend inspectors' authority. During active investigations, inspectors enjoy immunity.",
        "keywords": ["state inspectors", "compliance", "inspections", "regulatory enforcement", "legal expertise", "administrative fines", "governor authority", "government oversight", "investigation authority", "inspector immunity"]
    },
    "inspeqtorebisdepartamenti.txt": {
        "summary": "This law establishes the State Inspection Department under the Justice Department, independent from political pressure, to oversee state structures. The Department conducts audits, evaluates administrative activities, identifies systemic problems, and provides reform recommendations. It has authority for surprise inspections with 6-hour notice, access to all investigation information, and can impose sanctions. Violations are referred to prosecutors. Quarterly reports track recommendations' implementation.",
        "keywords": ["state inspection department", "oversight", "audits", "reform recommendations", "systematic evaluation", "administrative compliance", "sanctions authority", "prosecution referral", "transparency", "governmental accountability"]
    },
    "jildoebis.txt": {
        "summary": "This law regulates state and departmental awards/honors in San Andreas, with the Governor authorized to establish and present them. Medals are special honors for military service, labor achievement, and exceptional contributions. Other awards include commendation letters and honorary titles for public service. Courts may revoke awards as punishment for crimes violating honor. Recipients can recover lost award certificates. Awards may include privileges: tax exemptions, fee reductions, priority government services, and additional paid leave worth up to $100,000.",
        "keywords": ["state awards", "medals", "honors", "commendation", "governor authority", "official recognition", "award revocation", "privileges", "tax benefits", "honorary titles"]
    },
    "konstitucia.txt": {
        "summary": "The Constitution of San Andreas establishes the fundamental law and governmental structure based on democratic principles. It protects individual rights (life, liberty, property) and free speech. Government divides into three branches: Executive (Governor, Departments), Judicial (Supreme, Appellate, Trial Courts), and Legislative (Government Cabinet with advisory power). The Governor issues executive orders, appoints officials, uses National Guard, and grants pardons. The Attorney General heads Justice Department controlling prosecutors and police.",
        "keywords": ["constitution", "fundamental law", "government structure", "executive branch", "judicial branch", "legislative branch", "separation of powers", "governor authority", "individual rights", "democratic principles"]
    },
    "konstsasamartlos.txt": {
        "summary": "The Constitutional Court law establishes regulations for the highest court system, including roles of Chief Justice and Associate Justices, court structure, precedent authority, and judicial independence. The court reviews whether laws/acts comply with the constitution, interprets constitutional provisions, and can invalidate unconstitutional regulations. Justices have independence and cannot be pressured. The court system has specific procedures for cases and appeals.",
        "keywords": ["constitutional court", "judicial authority", "constitutional review", "legal precedent", "judicial independence", "court structure", "constitutional compliance", "interpretation authority", "unconstitutional acts", "appellate procedures"]
    },
    "marshalta.txt": {
        "summary": "This law establishes the US Marshals Service (USMS) as a law enforcement agency reporting to Governor and Lieutenant Governor. The USMS Director is appointed by Governor and supervises agents executing federal orders, finding/arresting fugitives, protecting court proceedings, investigating financial fraud, and protecting government officials. Agents can conduct searches, carry weapons, enter any property, and arrest citizens or government employees. USMS has federal jurisdiction across San Andreas and agent identities are classified.",
        "keywords": ["marshals service", "US marshals", "federal law enforcement", "fugitive apprehension", "court protection", "warrant execution", "federal authority", "arrest authority", "federal jurisdiction", "government protection"]
    },
    "mediis.txt": {
        "summary": "This law regulates state media (Weazel News) in San Andreas with government primary financial support. Media must serve public interest with accurate, unbiased reporting and transparency. Journalists must present credentials in restricted areas and obtain government-issued press passes. Justice Department can suspend media operations if they aid crimes or threaten state security/territorial integrity/public safety, with court review within one week. Media must publish official government notices for free.",
        "keywords": ["state media", "journalism", "press freedom", "media regulation", "government media", "press pass", "news access", "operational suspension", "official notices", "journalistic ethics"]
    },
    "mtavrob.txt": {
        "summary": "This law establishes San Andreas government structure based on democratic principles and constitutional foundations. Government coordinates executive departments (State, Homeland Security, Treasury, Culture, Justice) headed by Secretaries and Attorney General reporting to Governor. Government Cabinet meets to coordinate policy implementation. Governor leads Cabinet, appoints/removes officials, establishes strategic direction, coordinates emergency responses, and inspects departments. Lieutenant Governor assists and can assume duties during absence.",
        "keywords": ["government structure", "executive departments", "governor authority", "cabinet meetings", "department coordination", "emergency management", "official appointments", "strategic direction", "administrative coordination", "state operations"]
    },
    "policiis.txt": {
        "summary": "This law establishes Los Santos Police Department (LSPD) as primary law enforcement for Los Santos under Governor, Lieutenant Governor, and Attorney General oversight. LSPD Chief oversees all operations and subdepartments (SWAT names classified). Functions include crime prevention, emergency response, traffic control, community policing, and security at government events. Attorney General supervises LSPD through Justice Department. Citizens can file complaints with ombudsman or Attorney General. Internal inspection conducts audits.",
        "keywords": ["police department", "LSPD", "law enforcement", "crime prevention", "traffic control", "emergency response", "community policing", "disciplinary system", "oversight authority", "internal affairs", "public safety"]
    },
    "presisgivis.txt": {
        "summary": "This law guarantees freedom of press and mass media in San Andreas based on constitutional protection. Media includes newspapers, journals, TV/radio programs, and publications. The law prohibits censorship but allows restrictions if media aids crimes or endangers state security/territorial integrity/public safety. Justice Department can suspend media with court review within one week. Media must publish official government notices free. Journalists have rights to gather information and access institutions.",
        "keywords": ["press freedom", "media regulation", "freedom of speech", "journalism", "press rights", "media suspension", "journalistic responsibility", "official notices", "press credentials", "constitutional protection"]
    },
    "prokuraturis.txt": {
        "summary": "This law establishes the State Prosecutor's Office as the highest oversight body in San Andreas controlling law enforcement (police, FIB, federal prison) under the Attorney General. General Prosecutor reports exclusively to federal government and controls the entire prosecutorial system. Prosecutors monitor all state organs, enter any premises, demand documents/information, summon witnesses, conduct searches/arrests, and issue orders for violations. Prosecutors have immunity during duty except when drugs/mental state creates direct threat.",
        "keywords": ["prosecutor office", "attorney general", "oversight authority", "law enforcement control", "prosecution", "investigation authority", "federal jurisdiction", "prosecutorial immunity", "legal enforcement", "governmental control"]
    },
    "protokoli.txt": {
        "summary": "This law establishes emergency protocols for critical situations in San Andreas. Protocol White House activates when City Hall (Capitol) is seized, requiring all government structures to respond. Code Red activates for Fort Zancudo base attacks, requiring all law enforcement at the fortress within 5 minutes. Code Green activates for main bank robberies. Code Zero activates for casino heists. Each protocol specifies agency responsibilities, response times, and penalties ($100,000-$200,000 fines) for non-compliance.",
        "keywords": ["emergency protocols", "code red", "code green", "code zero", "white house protocol", "bank robbery response", "casino security", "fort zancudo", "emergency response", "protocol compliance"]
    },
    "saadvokato.txt": {
        "summary": "This Attorney Code regulates the legal profession, establishing requirements for attorney licensing, professional ethics for lawyers, and disciplinary procedures. It defines attorney-client privilege, attorney duties to provide qualified legal assistance, representation rights in courts, and requirements for bail/release requests. Attorneys must maintain competence through continuing education. The code specifies which criminal articles are eligible for bail release and establishes bail amount requirements.",
        "keywords": ["attorney code", "lawyers", "legal profession", "attorney licensing", "legal ethics", "attorney-client privilege", "legal practice", "lawyer discipline", "bail procedures", "court representation"]
    },
    "sagangebosaomari.txt": {
        "summary": "This law defines procedures for declaring and managing states of emergency and martial law in San Andreas. Emergency state can be declared for mass disorder, territorial integrity violations, coups, armed rebellions, terrorism, natural/technological disasters, or epidemics. Martial law applies to armed attacks or immediate threats. The law specifies conditions for declarations, temporary powers granted to authorities, suspension of certain rights, duration limits (3-72 hours for emergency, indefinite for martial law), and legislative oversight.",
        "keywords": ["state of emergency", "martial law", "emergency powers", "crisis management", "temporary authority", "rights suspension", "emergency declaration", "martial law declaration", "governor emergency powers", "public safety measures"]
    },
    "sagzao.txt": {
        "summary": "This comprehensive Road Code establishes traffic rules for Los Santos including vehicle types, driving obligations, traffic signals, speed limits (60 km/h in city, unlimited outside), lane requirements, parking restrictions, and pedestrian rights. The code mandates license documentation, vehicle registration numbers, drunk/drug-driving prohibitions, safe distances, and proper signaling. It establishes fines ranging from speeding ($2,500-$10,000) to dangerous driving ($20,000). Special vehicle privileges apply to emergency and government vehicles with blue/red lights.",
        "keywords": ["traffic laws", "vehicle code", "speed limits", "parking rules", "drunk driving", "traffic safety", "vehicle registration", "pedestrian rights", "traffic fines", "emergency vehicles", "road regulations"]
    },
    "saidumloebebi.txt": {
        "summary": "This law establishes classification levels for state secrets and official secrets, procedures for handling classified information, security clearance requirements, and penalties for unauthorized disclosure. State secrets include defense, economics, science/technology, foreign relations, and law enforcement information whose disclosure could harm national security. The law defines who has unrestricted access (Governor, Lieutenant Governor, Attorney General, etc.), protection measures for sensitive government information, and declassification procedures.",
        "keywords": ["state secrets", "classified information", "security clearance", "confidential documents", "information security", "disclosure penalties", "declassification", "official secrets", "access control", "national security information"]
    },
    "sakanshigantavsebis.txt": {
        "summary": "This law regulates the detention procedure for placing law violators in pre-trial detention facilities (jail). It establishes standards for inmate intake, body camera recording requirements during processing, medical examinations, prisoner rights notification, and documentation procedures. Officers must complete detention reports within 30 minutes of incarceration with specific format requirements. The law mandates body camera footage retention for 48 hours and defines sanctions for protocol violations under criminal code article 9.6.",
        "keywords": ["detention facilities", "pre-trial detention", "jail intake", "prisoner processing", "body camera requirements", "inmate rights", "detention reports", "medical examination", "custody procedures", "detention documentation"]
    },
    "samxrekameris.txt": {
        "summary": "This law mandates body camera (სამხრე კამერა) usage for all state structure employees in San Andreas. All government employees in official uniform must wear active body cameras during duty, especially during public contact, administrative actions, or procedural activities. Recordings must be stored minimum 48 hours. Exceptions: Government Cabinet members and Weazel News journalists. Violations result in disciplinary action, dismissal, or imprisonment under criminal code 9.6. If camera is damaged, employee must immediately stop duties and report.",
        "keywords": ["body camera", "bodycam", "mandatory recording", "government employees", "video evidence", "recording requirements", "camera footage", "evidence storage", "procedural recording", "accountability"]
    },
    "saproceso.txt": {
        "summary": "This is the Criminal Procedure Code that governs criminal justice procedures in San Andreas. It establishes rules for investigations, arrests, searches, warrants, evidence collection, interrogations, pre-trial detention, bail procedures, trial proceedings, and appeals. The code defines rights of suspects/defendants, prosecutor authority, defense attorney roles, court procedures, and sentencing guidelines. It ensures due process and fair trial rights throughout the criminal justice system.",
        "keywords": ["criminal procedure", "criminal justice", "investigations", "arrests", "warrants", "evidence", "trial proceedings", "due process", "defendants rights", "court procedures"]
    },
    "saprokuroroinspekcia.txt": {
        "summary": "This law establishes Prosecutor's Office inspection procedures for state organizations. The General Prosecutor and deputies are authorized to conduct planned and unplanned inspections to verify knowledge of laws, internal regulations, and professional skills. Planned inspections can occur max once per week per organization with 12-hour notice. Unplanned inspections require no notice and can be triggered by court decisions, violations, or investigations. Inspections use a 7-point system. Failing scores (1-2 points) result in dismissal/demotion.",
        "keywords": ["prosecutor inspection", "compliance inspection", "state organization oversight", "planned inspection", "unplanned inspection", "attorney general authority", "knowledge assessment", "disciplinary procedures", "inspection protocols", "organizational compliance"]
    },
    "saxelmwifoenis.txt": {
        "summary": "This law establishes English as the official state language of San Andreas (Los Santos). It defines state language status, usage requirements in government functions, and protection measures. The law mandates that state performs all functions in English, protects the language, and establishes language policy. All citizens must interact with state/municipal organs in the state language except in special cases. Public servants must know the state language. The law protects coexistence of languages and cultures while prohibiting disrespect toward any language.",
        "keywords": ["official language", "state language", "English language", "language policy", "government language", "language requirements", "public servants language", "language protection", "official communication", "language law"]
    },
    "shavisia.txt": {
        "summary": "This State Blacklist law establishes a government-maintained electronic list of individuals restricted from working in state structures for 3-15 days. Citizens are added to blacklist for criminal code violations with jail time or state contract violations. The duration varies: 3 days for contract violations, 5-10 days for non-federal criminal violations, 10-15 days for federal violations. Only high-ranking officials of the violator's organization can add entries (except Governor, Lieutenant Governor, Attorney General, Chief Justice who can add anyone). Only those four top officials can remove entries early.",
        "keywords": ["state blacklist", "employment restriction", "government blacklist", "state employment ban", "criminal record", "contract violations", "temporary ban", "blacklist duration", "employment eligibility", "state structure access"]
    },
    "shromis.txt": {
        "summary": "This Labor Code of San Andreas regulates employment relationships between employees and employers in government organizations. The Prosecutor's Office controls labor relations. The code covers employment principles (labor freedom, forced labor prohibition, discrimination ban, fair working conditions), employee/employer rights and obligations, working hours, rest periods, vacation rights, and compensation (hourly pay and bonuses). Employers must provide training, exams, and continuously improve organizations. Internal regulations require Attorney General approval.",
        "keywords": ["labor code", "employment law", "employee rights", "employer obligations", "working hours", "vacation rights", "compensation", "bonuses", "labor relations", "work discipline", "employment regulations"]
    },
    "simboloebi.txt": {
        "summary": "This law establishes state symbols of San Andreas including the state flag, state emblem, Governor's state seal, and state motto (\"In God We Trust\"). It regulates official symbols of government departments (Homeland Security, Treasury, State, Culture, Justice, Secret Service, Office of Inspector General) and allows state structures like LSPD, FIB, Weazel News, EMS, and National Guard to determine their own symbols via internal regulations. The law defines symbol creation, approval, and cancellation procedures requiring Governor's office and Government Cabinet approval.",
        "keywords": ["state symbols", "state flag", "state emblem", "state seal", "state motto", "government symbols", "department emblems", "official insignia", "symbol regulations", "heraldry"]
    },
    "sisxlissamartali.txt": {
        "summary": "This is the Criminal Code of San Andreas that defines all criminal offenses and their penalties. It categorizes crimes (minor, serious, grave, especially grave) and establishes punishments including fines, imprisonment, and federal charges. The code covers crimes against persons (murder, assault), property crimes (theft, robbery), public order offenses, crimes against justice, weapons violations, drug offenses, and federal crimes. It also defines mitigating/aggravating circumstances and punishment calculation methods.",
        "keywords": ["criminal code", "criminal offenses", "penalties", "imprisonment", "fines", "murder", "assault", "theft", "robbery", "federal crimes", "sentencing"]
    },
    "teritoriebis.txt": {
        "summary": "This law defines closed and protected territories with restricted access in San Andreas. It establishes three zone types: Red Zone (closed territory requiring organization employee escort for civilians, other agencies need official justification), Yellow Zone (additional security for state organization territories), and Green Zone (public access). The law specifies restricted areas for key facilities: EMS hospital, FIB headquarters, Government building (City Hall), with detailed access rules. Governor, Lieutenant Governor, Attorney General, Judges, and US Marshals have unrestricted access.",
        "keywords": ["restricted territories", "closed zones", "protected areas", "red zone", "yellow zone", "green zone", "restricted access", "facility security", "government buildings", "access control"]
    },
    "terorizmis.txt": {
        "summary": "This anti-terrorism law defines terrorist acts, establishes procedures for counter-terrorism operations, and outlines penalties for terrorism-related offenses. It covers terrorist organization membership, financing terrorism, terrorist propaganda, and acts intended to intimidate the population or compel government actions. The law grants law enforcement enhanced powers during anti-terrorism operations, establishes coordination mechanisms between agencies, and defines severe penalties including life imprisonment for terrorism crimes.",
        "keywords": ["terrorism", "anti-terrorism", "terrorist acts", "counter-terrorism", "terrorist organizations", "terrorism financing", "terrorist propaganda", "national security", "terrorism penalties", "anti-terrorism operations"]
    },
    "urtiertqmedebis.txt": {
        "summary": "This law regulates interactions and cooperation between different government agencies and structures in San Andreas. It establishes protocols for inter-agency communication, information sharing procedures, coordination mechanisms during joint operations, and jurisdictional boundaries between agencies. The law defines how agencies should request assistance from each other, protocols for joint task forces, and procedures for resolving jurisdictional disputes between different law enforcement or government bodies.",
        "keywords": ["inter-agency cooperation", "agency coordination", "information sharing", "joint operations", "jurisdictional boundaries", "inter-agency communication", "government cooperation", "agency assistance", "coordination protocols", "jurisdictional disputes"]
    },
    "USSS.txt": {
        "summary": "This law establishes the United States Secret Service (USSS) operating in San Andreas under the Department of Homeland Security with federal jurisdiction. USSS reports directly to Governor, Lieutenant Governor, and Homeland Security Secretary. Primary functions include protecting high-ranking officials (first responders), ensuring government building security, counter-terrorism, counter-intelligence, classified information protection, economic crime investigations, and court security. Agents have immunity during duty and their identities are classified. USSS has highest authority when protecting first responders.",
        "keywords": ["secret service", "USSS", "personal protection", "high official protection", "federal jurisdiction", "counter-terrorism", "classified information", "agent immunity", "government security", "VIP protection"]
    }
}


def add_metadata_to_file(filepath, metadata):
    """
    Add English metadata to a Georgian law file.

    Args:
        filepath: Path to the law file
        metadata: Dict with 'summary' and 'keywords' keys
    """
    # Read existing content
    with codecs.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if metadata already exists
    if "---METADATA---" in content:
        print(f"⚠️  Metadata already exists in {os.path.basename(filepath)}, replacing...")
        # Remove old metadata
        content = content.split("---METADATA---")[0].rstrip()

    # Format metadata
    metadata_text = f"""

---METADATA---
SUMMARY_EN: {metadata['summary']}

KEYWORDS_EN: {', '.join(metadata['keywords'])}
"""

    # Append metadata
    new_content = content + metadata_text

    # Write back
    with codecs.open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Added metadata to {os.path.basename(filepath)}")


def main():
    """Main function to process all law files."""
    laws_dir = "laws"

    if not os.path.exists(laws_dir):
        print(f"❌ Error: {laws_dir} directory not found!")
        return

    print("🚀 Starting metadata addition to all law files...\n")

    success_count = 0
    error_count = 0

    for filename, metadata in LAW_METADATA.items():
        filepath = os.path.join(laws_dir, filename)

        if not os.path.exists(filepath):
            print(f"❌ File not found: {filename}")
            error_count += 1
            continue

        try:
            add_metadata_to_file(filepath, metadata)
            success_count += 1
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Successfully processed: {success_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"📊 Total files in metadata dict: {len(LAW_METADATA)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
