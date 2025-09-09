#!/usr/bin/env python3
"""
Restore script to fix the SOLR document that was accidentally overwritten
"""

import json
import requests

def restore_fbbt_00003686():
    """Restore the original VFB data for FBbt_00003686"""
    
    # Original data from dev server
    original_doc = {
        "id": "FBbt_00003686",
        "anat_query": ["{\"term\": {\"core\": {\"iri\": \"http://purl.obolibrary.org/obo/FBbt_00003686\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Neuron\", \"Anatomy\", \"Cell\", \"Nervous_system\", \"has_subClass\", \"lineage_MBp\", \"hasScRNAseq\"], \"short_form\": \"FBbt_00003686\", \"unique_facets\": [\"Neuron\", \"lineage_MBp\"], \"label\": \"Kenyon cell\"}, \"description\": [\"Intrinsic neuron of the mushroom body. They have tightly-packed cell bodies, situated in the rind above the calyx of the mushroom body (Ito et al., 1997). Four short fascicles, one per lineage, extend from the cell bodies of the Kenyon cells into the calyx (Ito et al., 1997). These 4 smaller fascicles converge in the calyx where they arborize and form pre- and post-synaptic terminals (Christiansen et al., 2011), with different Kenyon cells receiving input in different calyx regions/accessory calyces (Tanaka et al., 2008). They emerge from the calyx as a thick axon bundle referred to as the peduncle that bifurcates to innervate the dorsal and medial lobes of the mushroom body (Tanaka et al., 2008).\"], \"comment\": [\"Pre-synaptic terminals were identified using two presynaptic markers (Brp and Dsyd-1) and post-synaptic terminals by labelling a subunit of the acetylcholine receptor (Dalpha7) in genetically labelled Kenyon cells (Christiansen et al., 2011).\"]}, \"query\": \"Get JSON for anat query\", \"version\": \"d3984f2\", \"anatomy_channel_image\": [{\"anatomy\": {\"symbol\": \"\", \"iri\": \"http://virtualflybrain.org/reports/VFB_001000o7\", \"types\": [\"Entity\", \"Individual\", \"VFB\", \"Neuron\", \"Adult\", \"Anatomy\", \"Cell\", \"Cholinergic\", \"Nervous_system\", \"has_image\", \"lineage_MBp\", \"has_neuron_connectivity\", \"FAFB\", \"NBLAST\"], \"short_form\": \"VFB_001000o7\", \"unique_facets\": [\"Adult\", \"Cholinergic\", \"lineage_MBp\"], \"label\": \"KC#705 (FAFB:8439172)\"}, \"channel_image\": {\"image\": {\"image_nrrd\": \"http://www.virtualflybrain.org/data/VFB/i/0010/00o7/VFB_00101567/volume.nrrd\", \"image_swc\": \"http://www.virtualflybrain.org/data/VFB/i/0010/00o7/VFB_00101567/volume.swc\", \"template_channel\": {\"symbol\": \"\", \"iri\": \"http://virtualflybrain.org/reports/VFBc_00101567\", \"types\": [\"Entity\", \"Individual\", \"VFB\", \"Channel\", \"Template\"], \"short_form\": \"VFBc_00101567\", \"unique_facets\": [\"Channel\"], \"label\": \"JRC2018Unisex_c\"}, \"index\": [], \"template_anatomy\": {\"symbol\": \"JRC2018U\", \"iri\": \"http://virtualflybrain.org/reports/VFB_00101567\", \"types\": [\"Entity\", \"Individual\", \"VFB\", \"Adult\", \"Anatomy\", \"Nervous_system\", \"Template\", \"has_image\"], \"short_form\": \"VFB_00101567\", \"unique_facets\": [\"Adult\", \"Nervous_system\"], \"label\": \"JRC2018Unisex\"}, \"image_wlz\": \"http://www.virtualflybrain.org/data/VFB/i/0010/00o6/VFB_00101567/volume.wlz\", \"image_obj\": \"http://www.virtualflybrain.org/data/VFB/i/0010/00o6/VFB_00101567/volume_man.obj\", \"image_thumbnail\": \"http://www.virtualflybrain.org/data/VFB/i/0010/00o6/VFB_00101567/thumbnail.png\", \"image_folder\": \"http://www.virtualflybrain.org/data/VFB/i/0010/00o6/VFB_00101567/\"}, \"channel\": {\"symbol\": \"\", \"iri\": \"http://virtualflybrain.org/reports/VFBc_001000o6\", \"types\": [\"Entity\", \"Individual\", \"VFB\", \"Channel\"], \"short_form\": \"VFBc_001000o6\", \"unique_facets\": [\"Channel\"], \"label\": \"KC#704_c\"}, \"imaging_technique\": {\"symbol\": \"TEM\", \"iri\": \"http://purl.obolibrary.org/obo/FBbi_00000258\", \"types\": [\"Entity\", \"Class\", \"has_subClass\"], \"short_form\": \"FBbi_00000258\", \"unique_facets\": [\"Class\"], \"label\": \"transmission electron microscopy (TEM)\"}}}]"],
        "anat_2_ep_query": ["{\"anatomy\": {\"iri\": \"http://purl.obolibrary.org/obo/FBbt_00003686\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Neuron\", \"Anatomy\", \"Cell\", \"Nervous_system\", \"has_subClass\", \"lineage_MBp\", \"hasScRNAseq\"], \"short_form\": \"FBbt_00003686\", \"unique_facets\": [\"Neuron\", \"lineage_MBp\"], \"label\": \"Kenyon cell\"}, \"expression_pattern\": {\"iri\": \"http://virtualflybrain.org/reports/VFBexp_FBti0002931\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Expression_pattern\"], \"short_form\": \"VFBexp_FBti0002931\", \"unique_facets\": [\"Expression_pattern\"], \"label\": \"P{GawB}30Y expression pattern\"}, \"query\": \"Get JSON for anat_2_ep query\", \"version\": \"d3984f2\", \"pubs\": [{\"core\": {\"iri\": \"http://flybase.org/reports/FBrf0098969\", \"symbol\": \"\", \"types\": [\"Entity\", \"Individual\", \"pub\"], \"short_form\": \"FBrf0098969\", \"unique_facets\": [\"pub\"], \"label\": \"Tettamanti et al., 1997, Dev. Genes Evol. 207(4): 242--252\"}, \"FlyBase\": \"FBrf0098969\", \"PubMed\": \"27747422\", \"DOI\": \"10.1007/s004270050112\"}], \"anatomy_channel_image\": []}"],
        "ep_2_anat_query": ["{\"anatomy\": {\"iri\": \"http://purl.obolibrary.org/obo/FBbt_00003686\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Neuron\", \"Anatomy\", \"Cell\", \"Nervous_system\", \"has_subClass\", \"lineage_MBp\", \"hasScRNAseq\"], \"short_form\": \"FBbt_00003686\", \"unique_facets\": [\"Neuron\", \"lineage_MBp\"], \"label\": \"Kenyon cell\"}, \"query\": \"Get JSON for ep_2_anat query\", \"version\": \"d3984f2\", \"pub\": {\"core\": {\"iri\": \"http://flybase.org/reports/FBrf0219767\", \"symbol\": \"\", \"types\": [\"Entity\", \"Individual\", \"pub\"], \"short_form\": \"FBrf0219767\", \"unique_facets\": [\"pub\"], \"label\": \"Krüttner et al., 2012, Neuron 76(2): 383--395\"}, \"FlyBase\": \"FBrf0219767\", \"PubMed\": \"23083740\", \"DOI\": \"10.1016/j.neuron.2012.08.028\"}, \"stages\": [], \"anatomy_channel_image\": []}"],
        "term_info": ["{\"term\": {\"core\": {\"iri\": \"http://purl.obolibrary.org/obo/FBbt_00003686\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Neuron\", \"Anatomy\", \"Cell\", \"Nervous_system\", \"has_subClass\", \"lineage_MBp\", \"hasScRNAseq\"], \"short_form\": \"FBbt_00003686\", \"unique_facets\": [\"Neuron\", \"lineage_MBp\"], \"label\": \"Kenyon cell\"}, \"description\": [\"Intrinsic neuron of the mushroom body. They have tightly-packed cell bodies, situated in the rind above the calyx of the mushroom body (Ito et al., 1997). Four short fascicles, one per lineage, extend from the cell bodies of the Kenyon cells into the calyx (Ito et al., 1997). These 4 smaller fascicles converge in the calyx where they arborize and form pre- and post-synaptic terminals (Christiansen et al., 2011), with different Kenyon cells receiving input in different calyx regions/accessory calyces (Tanaka et al., 2008). They emerge from the calyx as a thick axon bundle referred to as the peduncle that bifurcates to innervate the dorsal and medial lobes of the mushroom body (Tanaka et al., 2008).\"], \"comment\": [\"Pre-synaptic terminals were identified using two presynaptic markers (Brp and Dsyd-1) and post-synaptic terminals by labelling a subunit of the acetylcholine receptor (Dalpha7) in genetically labelled Kenyon cells (Christiansen et al., 2011).\"]}, \"query\": \"Get JSON for Neuron Class\", \"version\": \"d3984f2\", \"parents\": [{\"iri\": \"http://purl.obolibrary.org/obo/FBbt_00007484\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Neuron\", \"Anatomy\", \"Cell\", \"Nervous_system\", \"has_subClass\", \"hasScRNAseq\"], \"short_form\": \"FBbt_00007484\", \"unique_facets\": [\"Nervous_system\", \"Neuron\"], \"label\": \"mushroom body intrinsic neuron\"}, {\"iri\": \"http://purl.obolibrary.org/obo/FBbt_00025991\", \"symbol\": \"\", \"types\": [\"Entity\", \"Class\", \"Anatomy\", \"has_subClass\"], \"short_form\": \"FBbt_00025991\", \"unique_facets\": [\"Anatomy\"], \"label\": \"anterior ectoderm derivative\"}], \"relationships\": [{\"relation\": {\"iri\": \"http://purl.obolibrary.org/obo/RO_0002202\", \"database_cross_reference\": [], \"label\": \"develops from\", \"type\": \"develops_from\", \"confidence_value\": \"\"}, \"object\": {\"symbol\": \"\", \"iri\": \"http://purl.obolibrary.org/obo/FBbt_00007113\", \"types\": [\"Entity\", \"Class\", \"Anatomy\", \"Cell\", \"Nervous_system\", \"Neuroblast\", \"has_subClass\", \"lineage_MBp\"], \"short_form\": \"FBbt_00007113\", \"unique_facets\": [\"Class\"], \"label\": \"neuroblast MBp\"}}, {\"relation\": {\"iri\": \"http://purl.obolibrary.org/obo/RO_0002131\", \"database_cross_reference\": [], \"label\": \"overlaps\", \"type\": \"overlaps\", \"confidence_value\": \"\"}, \"object\": {\"symbol\": \"\", \"iri\": \"http://purl.obolibrary.org/obo/FBbt_00003687\", \"types\": [\"Entity\", \"Class\", \"Anatomy\", \"Nervous_system\", \"Synaptic_neuropil\", \"Synaptic_neuropil_domain\", \"has_subClass\"], \"short_form\": \"FBbt_00003687\", \"unique_facets\": [\"Nervous_system\", \"Synaptic_neuropil_domain\"], \"label\": \"mushroom body pedunculus\"}}, {\"relation\": {\"iri\": \"http://purl.obolibrary.org/obo/RO_0013002\", \"database_cross_reference\": [], \"label\": \"receives synaptic input in region\", \"type\": \"receives_synaptic_input_in_region\", \"confidence_value\": \"\"}, \"object\": {\"symbol\": \"\", \"iri\": \"http://purl.obolibrary.org/obo/FBbt_00003685\", \"types\": [\"Entity\", \"Class\", \"Anatomy\", \"Nervous_system\", \"Synaptic_neuropil\", \"Synaptic_neuropil_domain\", \"has_subClass\"], \"short_form\": \"FBbt_00003685\", \"unique_facets\": [\"Nervous_system\", \"Synaptic_neuropil_domain\"], \"label\": \"mushroom body calyx\"}}], \"related_individuals\": [], \"xrefs\": [], \"anatomy_channel_image\": [], \"pub_syn\": [], \"def_pubs\": [], \"targeting_splits\": []}"]
    }
    
    print("🔄 Restoring original VFB data for FBbt_00003686...")
    
    try:
        # Post the complete document to restore all original fields
        response = requests.post(
            "https://solr.virtualflybrain.org/solr/vfb_json/update/json/docs",
            json=[original_doc],
            headers={"Content-Type": "application/json"},
            params={"commit": "true"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Successfully restored original VFB data!")
            
            # Verify restoration
            verify_response = requests.get(
                "https://solr.virtualflybrain.org/solr/vfb_json/select",
                params={
                    "q": "id:FBbt_00003686",
                    "wt": "json",
                    "fl": "*"
                },
                timeout=10
            )
            
            if verify_response.status_code == 200:
                data = verify_response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    doc = docs[0]
                    field_count = len(doc)
                    original_fields = [k for k in doc.keys() if not k.startswith("vfb_query_") and k != "_version_"]
                    vfb_cache_fields = [k for k in doc.keys() if k.startswith("vfb_query_")]
                    
                    print(f"📊 Verification complete:")
                    print(f"   Total fields: {field_count}")
                    print(f"   Original VFB fields: {len(original_fields)} - {original_fields}")
                    print(f"   VFBquery cache fields: {len(vfb_cache_fields)} - {vfb_cache_fields}")
                    
                    if len(original_fields) >= 4:  # Should have id, anat_query, term_info, etc.
                        print("✅ Restoration successful - all original fields present!")
                    else:
                        print("⚠️  Restoration may be incomplete - some original fields missing")
        else:
            print(f"❌ Failed to restore: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Restoration error: {e}")

if __name__ == "__main__":
    restore_fbbt_00003686()
