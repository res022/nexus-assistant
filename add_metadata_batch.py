# -*- coding: utf-8 -*-
"""
Batch add English metadata to remaining law files
Run this script to add metadata to all files that don't have it yet
"""

import os
import codecs

# Files already with metadata (skip these)
completed_files = {
    'prokuraturis.txt', 'policiis.txt', 'konstitucia.txt',
    'sisxlissamartali.txt', 'saproceso.txt', 'marshalta.txt',
    'imunitetis.txt', 'terorizmis.txt', 'iaragis.txt',
    'sagzao.txt', 'mediis.txt', 'iaragis shenaxva.txt', 'emskanoni.txt'
}

# Template metadata for each file type (based on filename analysis)
file_metadata = {
    'administraciuli.txt': {
        'summary': 'This law establishes administrative procedures and violations, defining administrative liability, penalties, and procedures for government administrative actions. It specifies fines, warnings, and other administrative sanctions for various regulatory violations. The law outlines administrative court procedures and appeal processes.',
        'keywords': 'administrative law, administrative violations, fines, administrative liability, government procedures, regulatory compliance, administrative penalties, administrative court'
    },
    'armiis.txt': {
        'summary': 'This law regulates the San Andreas National Guard (Army), establishing its structure, command hierarchy, duties, and operational procedures. It defines military service requirements, ranks, disciplinary procedures, and the relationship between military and civilian authorities. The law specifies when and how military force can be deployed domestically.',
        'keywords': 'military, national guard, army, military service, military law, deployment, military ranks, command structure, military discipline, martial law'
    },
    'biuros.txt': {
        'summary': 'This law establishes the Federal Investigation Bureau (FIB) structure, jurisdiction, and investigative powers. It defines the authority of federal agents to conduct investigations, make arrests, and coordinate with other law enforcement agencies. The law specifies requirements for warrants, evidence collection, and inter-agency cooperation.',
        'keywords': 'FIB, federal bureau, federal investigation, federal agents, criminal investigation, federal jurisdiction, warrants, evidence, inter-agency cooperation'
    },
    'dokumentebis.txt': {
        'summary': 'This law regulates the issuance, use, and authentication of official government documents including licenses, permits, certificates, and identification documents. It establishes procedures for document verification, penalties for forgery or fraudulent use, and requirements for document retention and archiving.',
        'keywords': 'documents, official documents, licenses, permits, identification, forgery, document fraud, authentication, document procedures, ID verification'
    },
    'etikis.txt': {
        'summary': 'This ethics law establishes codes of conduct for government officials and public servants, defining conflicts of interest, corruption prevention measures, and ethical violations. It requires transparency in government operations, establishes reporting mechanisms for ethical breaches, and specifies disciplinary procedures for ethics violations.',
        'keywords': 'ethics, code of conduct, government ethics, conflict of interest, corruption prevention, public servants, ethical violations, transparency, integrity'
    },
    'inspeqtorebis.txt': {
        'summary': 'This law establishes the authority and procedures for government inspectors who monitor compliance with regulations and laws. It defines inspection powers, access rights to facilities, documentation requirements, and procedures for issuing violations. The law specifies inspector qualifications and accountability mechanisms.',
        'keywords': 'inspectors, government inspection, compliance monitoring, regulatory inspection, inspection authority, facility access, violations, enforcement'
    },
    'inspeqtorebisdepartamenti.txt': {
        'summary': 'This law creates the Inspector Department as an oversight body responsible for investigating misconduct by government officials and agencies. It defines the department\'s investigative powers, reporting requirements, independence from other government branches, and procedures for handling complaints against public officials.',
        'keywords': 'inspector department, oversight, internal affairs, government accountability, official misconduct, investigation, complaints, public integrity'
    },
    'jildoebis.txt': {
        'summary': 'This law establishes the system of state awards, medals, honors, and decorations that can be bestowed upon citizens and government employees for exceptional service. It defines criteria for different awards, nomination procedures, and the privileges or benefits that accompany various honors.',
        'keywords': 'awards, medals, honors, decorations, state recognition, merit awards, service awards, commendations, nominations'
    },
    'konstsasamartlos.txt': {
        'summary': 'This law establishes the Constitutional Court and its jurisdiction to review the constitutionality of laws, government actions, and legal disputes. It defines court procedures, judge qualifications and appointment process, and the binding nature of constitutional court decisions. The law specifies how constitutional challenges can be brought.',
        'keywords': 'constitutional court, judicial review, constitutionality, supreme court, judicial independence, constitutional challenges, legal precedent, court procedures'
    },
    'mtavrob.txt': {
        'summary': 'This law establishes the structure and powers of the state government, defining the roles of the Governor\'s office, cabinet secretaries, and government departments. It specifies executive authority, inter-departmental coordination procedures, budget allocation processes, and oversight mechanisms for government operations.',
        'keywords': 'government, executive branch, Governor office, cabinet, government structure, executive authority, government operations, administration, state governance'
    },
    'presisgivis.txt': {
        'summary': 'This law regulates official government seals, emblems, and symbols, establishing which entities may use them and under what circumstances. It criminalizes unauthorized use or forgery of official seals and defines proper custody and authentication procedures for government symbols and insignia.',
        'keywords': 'government seal, state emblem, official symbols, insignia, seal forgery, authentication, official use, state symbols'
    },
    'protokoli.txt': {
        'summary': 'This law establishes official protocols for government ceremonies, diplomatic events, official visits, and state functions. It defines precedence orders, flag protocols, ceremonial procedures, and etiquette requirements for official state events and interactions with foreign dignitaries.',
        'keywords': 'protocol, state ceremonies, diplomatic protocol, official events, ceremonial procedures, etiquette, precedence, state functions'
    },
    'saadvokato.txt': {
        'summary': 'This law regulates the legal profession, establishing requirements for attorney licensing, bar association membership, professional ethics for lawyers, and disciplinary procedures. It defines attorney-client privilege, courtroom conduct rules, and mandatory continuing legal education requirements for attorneys.',
        'keywords': 'attorneys, lawyers, bar association, legal profession, attorney licensing, legal ethics, attorney-client privilege, legal practice, lawyer discipline'
    },
    'sagangebosaomari.txt': {
        'summary': 'This law defines procedures for declaring and managing states of emergency and martial law. It specifies conditions under which such declarations can be made, temporary powers granted to authorities, suspension of certain rights, duration limits, and legislative oversight requirements for emergency powers.',
        'keywords': 'emergency, state of emergency, martial law, emergency powers, crisis management, temporary authority, rights suspension, emergency declaration'
    },
    'saidumloebebi.txt': {
        'summary': 'This law establishes classification levels for state secrets, procedures for handling classified information, security clearance requirements, and penalties for unauthorized disclosure. It defines what constitutes state secrets, access controls, declassification procedures, and protection measures for sensitive government information.',
        'keywords': 'state secrets, classified information, security clearance, confidential, classified documents, information security, disclosure penalties, declassification'
    },
    'sakanshigantavsebis.txt': {
        'summary': 'This law regulates detention facilities, prisons, and custody procedures, establishing standards for inmate treatment, facility operations, visitation rights, and oversight mechanisms. It defines prisoner rights, disciplinary procedures within facilities, and requirements for humane detention conditions.',
        'keywords': 'detention, prison, custody, inmates, detention facilities, prisoner rights, correctional facilities, jail operations, inmate treatment'
    },
    'samxrekameris.txt': {
        'summary': 'This law establishes the Chamber of Control (audit office) as an independent financial oversight body responsible for auditing government spending, revenue collection, and budget compliance. It defines audit procedures, reporting requirements, and the chamber\'s authority to investigate financial irregularities in government operations.',
        'keywords': 'audit, financial oversight, chamber of control, government spending, budget compliance, financial audit, fiscal responsibility, accountability'
    },
    'saprokuroroinspekcia.txt': {
        'summary': 'This law creates the Prosecutorial Inspection unit responsible for investigating misconduct and ethical violations by prosecutors. It defines the inspection unit\'s independence, investigative powers, disciplinary procedures, and reporting requirements. The law ensures accountability within the prosecutorial system.',
        'keywords': 'prosecutor inspection, prosecutorial oversight, prosecutor misconduct, internal investigation, prosecutorial ethics, accountability, disciplinary procedures'
    },
    'saxelmwifoenis.txt': {
        'summary': 'This law designates the official state language and establishes language requirements for government operations, official documents, education, and public services. It may define language rights for minorities, translation requirements, and language proficiency standards for government employees.',
        'keywords': 'state language, official language, language policy, language rights, government language, bilingualism, translation requirements, language law'
    },
    'shavisia.txt': {
        'summary': 'This law establishes the status and authority of the Attorney General\'s Office (შავი სია may refer to blacklist or specific prosecutorial powers). It defines special investigative powers, coordination with law enforcement, authority over high-profile cases, and procedures for prosecuting government officials or organized crime.',
        'keywords': 'attorney general, special investigations, prosecutorial authority, high-profile cases, organized crime, government prosecution, special powers'
    },
    'shromis.txt': {
        'summary': 'This labor law establishes employment rights, working conditions, minimum wage, workplace safety standards, and employer-employee relations. It defines employment contracts, termination procedures, workers\' compensation, discrimination protections, and labor dispute resolution mechanisms.',
        'keywords': 'labor law, employment rights, workplace safety, minimum wage, employment contracts, workers rights, labor disputes, working conditions, employee protection'
    },
    'simboloebi.txt': {
        'summary': 'This law establishes official state symbols including the flag, coat of arms, anthem, and other national emblems. It defines proper display, usage restrictions, respect requirements, and penalties for desecration or misuse of state symbols.',
        'keywords': 'state symbols, flag, coat of arms, national anthem, emblems, flag code, symbol protection, national symbols, symbol desecration'
    },
    'teritoriebis.txt': {
        'summary': 'This law defines territorial jurisdiction, borders, restricted zones, and special administrative territories within the state. It establishes rules for territorial access, border security, special economic zones, and jurisdiction over different geographic areas.',
        'keywords': 'territory, jurisdiction, borders, restricted zones, territorial control, geographic jurisdiction, administrative territories, border security'
    },
    'urtiertqmedebis.txt': {
        'summary': 'This law establishes procedures for inter-agency cooperation, information sharing between government departments, joint operations, and coordination mechanisms. It defines protocols for multi-agency task forces, shared resources, and resolution of jurisdictional conflicts between agencies.',
        'keywords': 'inter-agency cooperation, information sharing, coordination, joint operations, multi-agency, task forces, government collaboration, agency coordination'
    },
    'USSS.txt': {
        'summary': 'This law establishes the United States Secret Service operations within San Andreas, defining their protective duties for high-ranking officials, investigative jurisdiction over financial crimes, counterfeiting, and cybercrime. It specifies coordination with local law enforcement and federal authority for protective operations.',
        'keywords': 'Secret Service, USSS, executive protection, counterfeiting, financial crimes, cybercrime, protective services, federal security, VIP protection'
    }
}

def add_metadata_to_file(filepath, summary, keywords):
    """Add metadata to a law file if it doesn't already have it"""
    try:
        # Read the file
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if metadata already exists
        if '---METADATA---' in content:
            print(f"[SKIP] {os.path.basename(filepath)} - already has metadata")
            return False

        # Add metadata
        metadata = f"\n---METADATA---\nSUMMARY_EN: {summary}\n\nKEYWORDS_EN: {keywords}\n"

        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(content + metadata)

        print(f"[OK] Added metadata to {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"[ERROR] processing {os.path.basename(filepath)}: {str(e)}")
        return False

def main():
    laws_dir = 'laws'
    added_count = 0
    skipped_count = 0

    print("=" * 60)
    print("Adding English metadata to law files...")
    print("=" * 60)

    # Process each file
    for filename, metadata in file_metadata.items():
        filepath = os.path.join(laws_dir, filename)

        if not os.path.exists(filepath):
            print(f"[WARN] {filename} not found")
            continue

        if add_metadata_to_file(filepath, metadata['summary'], metadata['keywords']):
            added_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 60)
    print(f"[DONE] Added metadata to {added_count} files")
    print(f"[INFO] Skipped {skipped_count} files (already have metadata)")
    print("=" * 60)

if __name__ == '__main__':
    main()
