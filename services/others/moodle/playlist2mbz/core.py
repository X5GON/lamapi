import xml.etree.cElementTree as ET
import time
import datetime
import random
from pathlib import Path
from zipfile import ZipFile
import os
import copy
from shutil import rmtree
import string
import json

from components.dataconnection.index import get_resource_description, get_resource_metadata
from x5gonwp3tools.tools.difficulty.difficulty import __wpm, wikification2con_per_sec
from SETTINGS import EXP_IDS


# general settings
Path(f"tmp").mkdir(parents=True, exist_ok=True)
generated_folder = "tmp"


# Build the mbz from the plalist
def build_mbz(playlist_infos):
    # Generated course/context ids
    course_id = str(random.randint(10000, 100000))
    course_name = f"gdcrsx5pst_{course_id}"
    context_id = str(random.randint(10000, 100000))
    backup_timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    course_backupfile_name = f"backup-moodle2-course-{course_id}-{course_name}-{backup_timestamp}-nu"
    # Prepare folders structure
    Path(f"{generated_folder}/{course_backupfile_name}").mkdir(parents=True, exist_ok=True)
    Path(f"{generated_folder}/{course_backupfile_name}/activities").mkdir(parents=True, exist_ok=True)
    Path(f"{generated_folder}/{course_backupfile_name}/course").mkdir(parents=True, exist_ok=True)
    Path(f"{generated_folder}/{course_backupfile_name}/sections").mkdir(parents=True, exist_ok=True)
    open(f"{generated_folder}/{course_backupfile_name}/moodle_backup.xml", mode='w', buffering=-1, encoding=None)
    # Needed file for X5gon moodle plugin
    open(f"{generated_folder}/{course_backupfile_name}/plst.json", mode='w', buffering=-1, encoding=None)
    # Prepare the playlist items
    playlist_general_infos = playlist_infos['playlist_general_infos']
    # Get resource list from playlist (from service input)
    playlist_enriched = enrich_playlist_items(playlist_infos)
    with open(f"{generated_folder}/{course_backupfile_name}/plst.json", 'w') as fp:
        json.dump(playlist_enriched, fp)
    playlist_items = playlist_enriched['playlist_items']
    # General course infos
    crs_str_from_pst = generate_needed_ids(playlist_items, playlist_general_infos)
    course_infos = {"crs_full_name": f"{playlist_general_infos['pst_name']}",
                    "crs_short_name": f"{course_name}",
                    "crs_id": f"{course_id}",
                    "crs_context_id": f"{context_id}",
                    "crs_bkp_name": f"{course_backupfile_name}",
                    "crs_bkp_timestamp": f"{backup_timestamp}",
                    "crs_playlist_url": f"{playlist_general_infos['pst_url']}",
                    "crs_sections": crs_str_from_pst
                   }
    try:
        # Generate needed files
        generate_mdl_bkpfile(ET, course_infos)
        # Generated the compressed mbz file
        compress_folder(course_backupfile_name)
        return {"mbz_build": "success",
                "directory": "tmp",
                "filename": f"{course_backupfile_name}.mbz",
                "mbz_folder": f"{course_backupfile_name}",
                "plst_obj": playlist_enriched,
                "error": ""
                }
    except Exception as e:
        print(e)
        return {"mbz_build": "failed",
                "error": f"error occured: {e}"}


def enrich_playlist_items(playlist_infos):
    pst_items_ix = [{'x5gon_id': item['x5gon_id'],
                     'xlearn_id': item['material_id'],
                     'item_ix': i}
                    for i, item in enumerate(playlist_infos['playlist_items'])]
    x5gon_items_ix = [item
                      for item in pst_items_ix
                      if item['x5gon_id'] not in [None, 'null', '']
                     ]
    resources_ids = [item['x5gon_id'] for item in x5gon_items_ix]
    resources_needed_infos = get_resource_description(resources_ids,
                                                      {"concepts": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                                                       "keywords": EXP_IDS['text2tfidf']['SIMPLE']['experiment_id']},
                                                       max_concepts=5,
                                                       max_keywords=5)
    res_metadata = get_resource_metadata(resources_ids)
    resources_final_infos = []
    for i, pstx5item in enumerate(x5gon_items_ix):
        rid = pstx5item['x5gon_id']
        rix = pstx5item['item_ix']
        res_infos = resources_needed_infos.get(int(rid), dict())
        res_metainfos = res_metadata.get(int(rid), dict())
        # The following metadata will be fetched directly from the plalist infos
        if 'title' not in playlist_infos['playlist_items'][rix] or playlist_infos['playlist_items'][rix]['title'] is None:
            playlist_infos['playlist_items'][rix]['title'] = res_metainfos['title'] if res_metainfos['title'] is not None else ''
        if 'description' not in playlist_infos['playlist_items'][rix] or playlist_infos['playlist_items'][rix]['description'] is None:
            playlist_infos['playlist_items'][rix]['description'] = ' '.join(res_metainfos['description'].split()[:150]) if res_metainfos['description'] is not None else ''
        if 'duration' not in playlist_infos['playlist_items'][rix] or playlist_infos['playlist_items'][rix]['duration'] in [None, '']:
            playlist_infos['playlist_items'][rix]['duration'] = f"~ {res_metainfos['len_word'] / __wpm()['Slide']} mins" if 'len_word' in res_metainfos else "~ unknown"
        playlist_infos['playlist_items'][rix]['url'] = res_metainfos['url'] if 'url' in res_metainfos else playlist_infos['playlist_items'][rix]['url']
        playlist_infos['playlist_items'][rix]['author'] = ", ".join(res_metainfos['authors']) if ('authors' in res_metainfos and res_metainfos['authors'] is not None) else ''
        playlist_infos['playlist_items'][rix]['date'] = res_metainfos['date'] if ('date' in res_metainfos and res_metainfos['date'] not in ['', None]) else (playlist_infos['playlist_items'][rix]['date'] if 'date' in playlist_infos['playlist_items'][rix] else '')
        playlist_infos['playlist_items'][rix]['mediatype'] = res_metainfos['type'] if ('type' in res_metainfos and res_metainfos['type'] !='') else playlist_infos['playlist_items'][rix]['mediatype']
        playlist_infos['playlist_items'][rix]['license'] = res_metainfos['license'] if ('license' in  res_metainfos and res_metainfos['license'] is not None) else ''
        # This is to make sure that there is no "" chars can brake the xmls
        playlist_infos['playlist_items'][rix]['title'] = ''.join(filter(lambda x: x in string.printable, playlist_infos['playlist_items'][rix]['title'].replace('"',"")))
        playlist_infos['playlist_items'][rix]['description'] = ''.join(filter(lambda x: x in string.printable, playlist_infos['playlist_items'][rix]['description'].replace('"',"")))
        if res_infos:
            res_infos['difficulty'] = wikification2con_per_sec(res_infos['len_char'], res_infos['len_concepts'])
            del res_infos['keywords_full']
            del res_infos['wikifier_full']
            # update only the metadata of the found oers in db
            playlist_infos['playlist_items'][rix]['difficulty'] = res_infos['difficulty']
            playlist_infos['playlist_items'][rix]['keywords'] = ", ".join([keyword['label'] for i, keyword in enumerate(res_infos['keywords'])])
            playlist_infos['playlist_items'][rix]['concepts'] = res_infos['wikifier']
        else:
            playlist_infos['playlist_items'][rix]['difficulty'] = ''
            playlist_infos['playlist_items'][rix]['keywords'] = ''
            playlist_infos['playlist_items'][rix]['concepts'] = []
        resources_final_infos.append(res_infos)
    return playlist_infos


def clean_mbz(mbz_path):
    Path(f"{generated_folder}/{mbz_path}.mbz").unlink()
    rmtree(f"{generated_folder}/{mbz_path}")


def generate_mdl_bkpfile(ET, course_infos):
    moodle_backup = ET.Element("moodle_backup")
    information = ET.SubElement(moodle_backup, "information")
    ET = mdl_bkfile_geninfosec(ET, information, course_infos)
    details = ET.SubElement(information, "details")
    ET = mdl_bklfile_detailssec(ET, details)
    contents = ET.SubElement(information, "contents")
    ET = mdl_bklfile_contentssec(ET, contents, course_infos)
    settings = ET.SubElement(information, "settings")
    ET = mdl_bklfile_settingssec(ET, settings, course_infos)

    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/moodle_backup.xml", moodle_backup)

    # Populate the other backupfiles
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/roles.xml", mode='w', buffering=-1, encoding=None)
    roles = ET.Element("roles_definition")
    role = ET.SubElement(roles, "role", id='5')
    ET.SubElement(role, "name").text = ''
    ET.SubElement(role, "shortname").text = 'student'
    ET.SubElement(role, "nameincourse").text = '$@NULL@$'
    ET.SubElement(role, "description").text = ''
    ET.SubElement(role, "sortorder").text = '5'
    ET.SubElement(role, "archtype").text = 'student'
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/roles.xml", roles)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/scales.xml", mode='w', buffering=-1, encoding=None)
    scales = ET.Element("scales_definition")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/scales.xml", scales)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/completion.xml", mode='w', buffering=-1, encoding=None)
    completion = ET.Element("course_completion")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/completion.xml", completion)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/questions.xml", mode='w', buffering=-1, encoding=None)
    questions = ET.Element("question_categories")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/questions.xml", questions)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/outcomes.xml", mode='w', buffering=-1, encoding=None)
    outcomes = ET.Element("outcomes_definition")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/outcomes.xml", outcomes)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/groups.xml", mode='w', buffering=-1, encoding=None)
    groups = ET.Element("groups")
    ET.SubElement(groups, "groupings")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/groups.xml", groups)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/files.xml", mode='w', buffering=-1, encoding=None)
    files = ET.Element("files")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/files.xml", files)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/grade_history.xml", mode='w', buffering=-1, encoding=None)
    grade_history = ET.Element("grade_history")
    ET.SubElement(grade_history, "grade_grades")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/grade_history.xml", grade_history)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/gradebook.xml", mode='w', buffering=-1, encoding=None)
    gradebook = ET.Element("gradebook")
    ET.SubElement(gradebook, "attributes")
    ET.SubElement(gradebook, "grade_categories")
    ET.SubElement(gradebook, "grade_items")
    ET.SubElement(gradebook, "grade_letters")
    grade_settings = ET.SubElement(gradebook, "grade_settings")
    grade_setting = ET.SubElement(grade_settings, "grade_setting", id='')
    ET.SubElement(grade_setting, "name").text = 'minmaxtouse'
    ET.SubElement(grade_setting, "value").text = '1'
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/gradebook.xml", gradebook)


def writetoxml_update_needed_mdl_header(xml_file_name, xml_content):
    # Write to xml file
    xml_tree = ET.ElementTree(xml_content)
    xml_tree.write(xml_file_name,
                   xml_declaration=True,
                   encoding="UTF-8",
                   method="xml")
    # Fix header
    xml_file = open(xml_file_name,'r')
    old = xml_file.read()
    new = old.replace("<?xml version='1.0' encoding='UTF-8'?>", '<?xml version="1.0" encoding="UTF-8"?>')
    xml_file = open(xml_file_name,'w')
    xml_file.write(new)


def compress_folder(dirName):
    # create a ZipFile object
    with ZipFile(f"{generated_folder}/{dirName}.mbz", 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(f"{generated_folder}/{dirName}/"):
            for filename in filenames:
                # create complete filepath of file in directory
                filepath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filepath, os.path.relpath(filepath, f"{generated_folder}/{dirName}/"))


def generate_needed_ids(playlist_items, playlist_general_infos):
    # Our vision of crs structure
    # general structure infos
    sec_items1 = copy.deepcopy(playlist_items)
    sec_items2 = copy.deepcopy(playlist_items)
    crs_structure = [{   "sec_label": 'abstract',
                         "sec_title": 'Abstract',
                         "sec_summary": f"This is an auto-generated course from Xlearn playlist: {playlist_general_infos['pst_name']}",
                         "sec_order": "0",
                         "sec_activities": [],
                         "sec_activity_descstyle": "bullets",
                         "sec_extra_infos": {"Title": f"{playlist_general_infos['pst_name']}",
                                             "Description": f"{playlist_general_infos['pst_description']}",
                                             "Author": f"{playlist_general_infos['pst_author']}",
                                             "Creation date": f"{playlist_general_infos['pst_creation_date']}",
                                             "License": f"{playlist_general_infos['pst_license']}",
                                             "Url": f"{playlist_general_infos['pst_url']}"
                                             # "Thumbnail": f"{playlist_general_infos['pst_thumbnail_url']}"
                                            }
                     },
                     {
                         "sec_label": 'main',
                         "sec_title": 'Playlist presentation',
                         "sec_summary": 'Here are the playlist items:',
                         "sec_order": "1",
                         "sec_activities": sec_items1,
                         "sec_activity_descstyle": "table",
                         "sec_extra_infos": {}
                     }
                    # ,{
                    #      "sec_label": 'main1',
                    #      "sec_title": 'Playlist presentation',
                    #      "sec_summary": 'Here are the playlist items:',
                    #      "sec_order": "2",
                    #      "sec_activities": sec_items2,
                    #      "sec_activity_descstyle": "bullets",
                    #      "sec_extra_infos": {}
                    #  }
                     ]
    # Generate random section ids
    sections_rand_id = random.sample(range(1000), len(crs_structure))
    for k, sec_infos in enumerate(crs_structure):
        sec_infos['sec_id'] = str(sections_rand_id[k])
        activities_rand_id = random.sample(range(1000), len(sec_infos['sec_activities']))
        for i, res in enumerate(sec_infos['sec_activities']):
            res['generated_activity_id'] = str(activities_rand_id[i])
            res['generated_section_id'] = str(sec_infos['sec_id'])
            res['activity_descstyle'] = sec_infos['sec_activity_descstyle']
    return crs_structure


def mdl_bkfile_geninfosec(ET, information, course_infos):
    ET.SubElement(information, "name").text = f"{course_infos['crs_bkp_name']}.mbz"
    ET.SubElement(information, "moodle_version").text = "2018120303.12"
    ET.SubElement(information, "moodle_release").text = "3.6.3+ (Build: 20190423)"
    ET.SubElement(information, "backup_version").text = "2018120300"
    ET.SubElement(information, "backup_release").text = "3.6"
    ET.SubElement(information, "backup_date").text = str(int(time.time()))
    ET.SubElement(information, "mnet_remoteusers").text = "0"
    ET.SubElement(information, "include_files").text = "1"
    ET.SubElement(information, "include_file_references_to_external_content").text = "0"
    ET.SubElement(information, "original_wwwroot").text = "<a href='http://x5gon.org' target='_blank'>x5gon.org</a>"
    ET.SubElement(information, "original_site_identifier_hash").text = "a48d6267a5fc08d341e51ba07b19ba7d48f3e66e"
    ET.SubElement(information, "original_course_id").text = course_infos['crs_id']
    ET.SubElement(information, "original_course_format").text = "topics"
    ET.SubElement(information, "original_course_fullname").text = f"{course_infos['crs_full_name']}"
    ET.SubElement(information, "original_course_shortname").text = f"{course_infos['crs_short_name']}"
    ET.SubElement(information, "original_course_startdate").text = str(int(time.time()))
    ET.SubElement(information, "original_course_enddate").text = "0"
    ET.SubElement(information, "original_course_contextid").text = f"{course_infos['crs_context_id']}"
    ET.SubElement(information, "original_system_contextid").text = "1"
    return ET


def mdl_bklfile_detailssec(ET, details):
    detail = ET.SubElement(details, "detail", name="4ab9f7c4a0efca1acfd034ba23c58440")
    ET.SubElement(detail, "type").text = "course"
    ET.SubElement(detail, "format").text = "moodle2"
    ET.SubElement(detail, "interactive").text = "1"
    ET.SubElement(detail, "mode").text = "10"
    ET.SubElement(detail, "execution").text = "1"
    ET.SubElement(detail, "executiontime").text = "0"
    return ET


def mdl_bklfile_contentssec(ET, contents, course_infos):
    # For our case: all activities are in the same section
    ## sec_id = resources[1]['generated_section_id']
    ## activities_rand_id = [res['generated_activity_id'] for res in resources]
    # Activities sub-section
    activities = ET.SubElement(contents, "activities")
    sections_infos = course_infos['crs_sections']
    for k, sec_infos in enumerate(sections_infos):
        for i, res in enumerate(sec_infos['sec_activities']):
            ET = mdl_bklfile_activitysec(ET, activities, res, sec_infos['sec_id'], res['generated_activity_id'], course_infos)
    # Sections sub-section
    sections = ET.SubElement(contents, "sections")
    for i, sec_infos in enumerate(sections_infos):
        ET = mdl_bklfile_sectionsec(ET, sections, sec_infos, course_infos)
    # Course sub-section
    course = ET.SubElement(contents, "course")
    ET = mdl_bklfile_coursesec(ET, course, course_infos)
    return ET


def mdl_bklfile_settingssec(ET, settings, course_infos):
    # For our case: all activities are in the same section
    sections = course_infos['crs_sections']
    # general settings
    gen_settings = [
                        {"level":"root", "name":"filename", "value":"0"},
                        {"level":"root", "name":"imscc11", "value":"0"},
                        {"level":"root", "name":"users", "value":"0"},
                        {"level":"root", "name":"anonymize", "value":"0"},
                        {"level":"root", "name":"role_assignments", "value":"0"},
                        {"level":"root", "name":"activities", "value":"1"},
                        {"level":"root", "name":"blocks", "value":"0"},
                        {"level":"root", "name":"filters", "value":"0"},
                        {"level":"root", "name":"comments", "value":"0"},
                        {"level":"root", "name":"badges", "value":"0"},
                        {"level":"root", "name":"calendarevents", "value":"0"},
                        {"level":"root", "name":"userscompletion", "value":"0"},
                        {"level":"root", "name":"logs", "value":"0"},
                        {"level":"root", "name":"grade_histories", "value":"0"},
                        {"level":"root", "name":"questionbank", "value":"0"},
                        {"level":"root", "name":"groups", "value":"0"},
                        {"level":"root", "name":"competencies", "value":"0"}
                ]
    # general settings
    for i, sett in enumerate(gen_settings):
        setting = ET.SubElement(settings, "setting")
        for key in sett.keys():
            ET.SubElement(setting, key).text = sett[key]
    # sections settings
    for k, sec_infos in enumerate(sections):
        setting = ET.SubElement(settings, "setting")
        sec_id = sec_infos['sec_id']
        ET.SubElement(setting, "level").text = "section"
        ET.SubElement(setting, "section").text = f"section_{sec_id}"
        ET.SubElement(setting, "name").text = f"section_{sec_id}_included"
        ET.SubElement(setting, "value").text = "1"
        setting = ET.SubElement(settings, "setting")
        ET.SubElement(setting, "level").text = "section"
        ET.SubElement(setting, "section").text = f"section_{sec_id}"
        ET.SubElement(setting, "name").text = f"section_{sec_id}_userinfo"
        ET.SubElement(setting, "value").text = "0"
    # activities settings
    for k, sec_infos in enumerate(sections):
        resources = sec_infos['sec_activities']
        for i, res in enumerate(resources):
            setting = ET.SubElement(settings, "setting")
            activity_id = res['generated_activity_id']
            ET.SubElement(setting, "level").text = "activity"
            ET.SubElement(setting, "activity").text = f"url_{activity_id}"
            ET.SubElement(setting, "name").text = f"url_{activity_id}_included"
            ET.SubElement(setting, "value").text = "1"
            setting = ET.SubElement(settings, "setting")
            ET.SubElement(setting, "level").text = "activity"
            ET.SubElement(setting, "activity").text = f"url_{activity_id}"
            ET.SubElement(setting, "name").text = f"url_{activity_id}_userinfo"
            ET.SubElement(setting, "value").text = "0"
    return ET


def mdl_bklfile_coursesec(ET, course, course_infos):
    ET.SubElement(course, "courseid").text = course_infos['crs_id']
    ET.SubElement(course, "title").text = course_infos['crs_short_name']
    ET.SubElement(course, "directory").text = "course"
    # Generate the related files
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/course.xml", mode='w', buffering=-1, encoding=None)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/inforef.xml", mode='w', buffering=-1, encoding=None)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/roles.xml", mode='w', buffering=-1, encoding=None)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/enrolments.xml", mode='w', buffering=-1, encoding=None)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/completiondefaults.xml", mode='w', buffering=-1, encoding=None)
    mdl_crsfile(course_infos)
    return ET


def mdl_crsfile(course_infos):
    course = ET.Element("course", id=course_infos['crs_id'], contextid=course_infos['crs_context_id'])
    ET.SubElement(course, "shortname").text = course_infos['crs_short_name']
    ET.SubElement(course, "fullname").text = course_infos['crs_full_name']
    ET.SubElement(course, "idnumber").text = ''
    ET.SubElement(course, "summary").text = ''
    ET.SubElement(course, "summaryformat").text = '1'
    ET.SubElement(course, "format").text = 'topics'
    ET.SubElement(course, "showgrades").text = '1'
    ET.SubElement(course, "newsitems").text = '5'
    ET.SubElement(course, "startdate").text = str(int(time.time()))
    ET.SubElement(course, "enddate").text = '0'
    ET.SubElement(course, "marker").text = '0'
    ET.SubElement(course, "maxbytes").text = '0'
    ET.SubElement(course, "legacyfiles").text = '0'
    ET.SubElement(course, "showreports").text = '0'
    ET.SubElement(course, "visible").text = '1'
    ET.SubElement(course, "groupmode").text = '0'
    ET.SubElement(course, "groupmodeforce").text = '0'
    ET.SubElement(course, "defaultgroupingid").text = '0'
    ET.SubElement(course, "lang").text = ''
    ET.SubElement(course, "theme").text = ''
    ET.SubElement(course, "timecreated").text = str(int(time.time()))
    ET.SubElement(course, "timemodified").text = str(int(time.time()))
    ET.SubElement(course, "requested").text = '0'
    ET.SubElement(course, "enablecompletion").text = '1'
    ET.SubElement(course, "completionnotify").text = '0'
    ET.SubElement(course, "hiddensections").text = '0'
    ET.SubElement(course, "coursedisplay").text = '0'
    ET.SubElement(course, "tags").text = ''
    category = ET.SubElement(course, "category", id="10000")
    ET.SubElement(category, "name").text = 'x5gonDefaultCategory'
    ET.SubElement(category, "description").text = 'X5GON Default Category'
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/course.xml", course)

    # Populate the other course files
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/inforef.xml", mode='w', buffering=-1, encoding=None)
    inforef = ET.Element("inforef")
    roleref = ET.SubElement(inforef, "roleref")
    role = ET.SubElement(roleref, "role")
    ET.SubElement(role, "id").text = '5'
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/inforef.xml", inforef)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/roles.xml", mode='w', buffering=-1, encoding=None)
    roles = ET.Element("roles")
    role_overrides = ET.SubElement(roles, "role_overrides")
    role_assignments = ET.SubElement(roles, "role_assignments")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/roles.xml", roles)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/completiondefaults.xml", mode='w', buffering=-1, encoding=None)
    course_completion_defaults = ET.Element("course_completion_defaults")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/completiondefaults.xml", course_completion_defaults)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/enrolments.xml", mode='w', buffering=-1, encoding=None)
    mdl_enrolmentsfile(course_infos)


def mdl_enrolmentsfile(course_infos):
    enrolments = ET.Element("enrolments")
    enrols = ET.SubElement(enrolments, "enrols")
    enrolment_ids = [13, 14, 15]
    for i, enr in enumerate(enrolment_ids):
        enrol = ET.SubElement(enrols, "enrol", id=str(enr))
        ET.SubElement(enrol, "enrol").text = 'manual'
        ET.SubElement(enrol, "status").text = '0'
        ET.SubElement(enrol, "name").text = '$@NULL@$'
        ET.SubElement(enrol, "enrolperiod").text = '0'
        ET.SubElement(enrol, "enrolstartdate").text = '0'
        ET.SubElement(enrol, "enrolenddate").text = '0'
        ET.SubElement(enrol, "expirynotify").text = '86400'
        ET.SubElement(enrol, "expirythreshold").text = '0'
        ET.SubElement(enrol, "notifyall").text = 'x5gon Default Category'
        ET.SubElement(enrol, "password").text = '$@NULL@$'
        ET.SubElement(enrol, "cost").text = '$@NULL@$'
        ET.SubElement(enrol, "currency").text = '$@NULL@$'
        ET.SubElement(enrol, "roleid").text = '5'
        ET.SubElement(enrol, "customint1").text ='$@NULL@$'
        ET.SubElement(enrol, "customint2").text = '$@NULL@$'
        ET.SubElement(enrol, "customint3").text = '$@NULL@$'
        ET.SubElement(enrol, "customint4").text = '$@NULL@$'
        ET.SubElement(enrol, "customint5").text = '$@NULL@$'
        ET.SubElement(enrol, "customint6").text ='$@NULL@$'
        ET.SubElement(enrol, "customint7").text = '$@NULL@$'
        ET.SubElement(enrol, "customint8").text = '$@NULL@$'
        ET.SubElement(enrol, "customchar1").text = '$@NULL@$'
        ET.SubElement(enrol, "customchar2").text = '$@NULL@$'
        ET.SubElement(enrol, "customchar3").text = '$@NULL@$'
        ET.SubElement(enrol, "customdec1").text = '$@NULL@$'
        ET.SubElement(enrol, "customdec2").text = '$@NULL@$'
        ET.SubElement(enrol, "customtext1").text = '$@NULL@$'
        ET.SubElement(enrol, "customtext2").text = '$@NULL@$'
        ET.SubElement(enrol, "customtext3").text = '$@NULL@$'
        ET.SubElement(enrol, "customtext4").text = '$@NULL@$'
        ET.SubElement(enrol, "timecreated").text = '$@NULL@$'
        ET.SubElement(enrol, "timemodified").text = str(int(time.time()))
        ET.SubElement(enrol, "user_enrolments").text = '1584886679'
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/course/enrolments.xml", enrolments)


def mdl_bklfile_sectionsec(ET, sections, sec_infos, course_infos):
    sec_id = sec_infos['sec_id']
    activities_id = [act['generated_activity_id'] for act in sec_infos['sec_activities']]
    section = ET.SubElement(sections, "section")
    ET.SubElement(section, "sectionid").text = sec_id
    ET.SubElement(section, "title").text = sec_infos['sec_title']
    ET.SubElement(section, "directory").text = f"sections/section_{sec_id}"
    # Generate the related files
    Path(f"{generated_folder}/{course_infos['crs_bkp_name']}/sections/section_{sec_id}").mkdir(parents=True, exist_ok=True)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/sections/section_{sec_id}/section.xml", mode='w', buffering=-1, encoding=None)
    mdl_sectfile(sec_infos, activities_id, course_infos)
    # populate the other section files
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/sections/section_{sec_id}/inforef.xml", mode='w', buffering=-1, encoding=None)
    inforef = ET.Element("inforef")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/sections/section_{sec_id}/inforef.xml", inforef)
    return ET


def mdl_sectfile(sec_infos, activities_id, course_infos):
    sec_id = sec_infos['sec_id']
    section = ET.Element("section", id=sec_id)
    ET.SubElement(section, "number").text = f"{sec_infos['sec_order']}"
    ET.SubElement(section, "name").text = f"{sec_infos['sec_title']}"
    ET.SubElement(section, "summary").text = f"{fill_sec_summary(sec_infos)}"
    ET.SubElement(section, "summaryformat").text = '1'
    ET.SubElement(section, "sequence").text = ','.join( str(act) for act in activities_id)
    ET.SubElement(section, "visible").text = '1'
    ET.SubElement(section, "availabilityjson").text = '$@NULL@$'
    ET.SubElement(section, "timemodified").text = str(int(time.time()))
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/sections/section_{sec_id}/section.xml", section)


def fill_sec_summary(sec_infos):
    summary = f"<div>{sec_infos['sec_summary']}</div>"
    if sec_infos['sec_label'] == 'abstract':
        summary+= "<div><ul>"
        for key in sec_infos['sec_extra_infos'].keys():
            summary+= "<li>"
            if key =='Url':
                summary+= f"{key}: <a href='http://{sec_infos['sec_extra_infos'][key]}' target='_blank'>{sec_infos['sec_extra_infos'][key]}</a>"
            else:
                summary+= f"{key}: {sec_infos['sec_extra_infos'][key]}"
            summary+= "</li>"
        summary+= "</ul></div>"
    return summary


def mdl_bklfile_activitysec(ET, activities, resource_info, sec_id, activity_id, course_infos):
    activity = ET.SubElement(activities, "activity")
    ET.SubElement(activity, "moduleid").text = activity_id
    ET.SubElement(activity, "sectionid").text = sec_id
    ET.SubElement(activity, "modulename").text = "url"
    ET.SubElement(activity, "title").text = resource_info['title'] if resource_info['title'] != '' else resource_info['url']
    ET.SubElement(activity, "directory").text = f"activities/url_{activity_id}"
    # Generate the related files
    Path(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}").mkdir(parents=True, exist_ok=True)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/module.xml", mode='w', buffering=-1, encoding=None)
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/url.xml", mode='w', buffering=-1, encoding=None)
    # poulate the needed files
    mdl_modulefile(sec_id, activity_id, course_infos)
    mdl_activityfile(sec_id, activity_id, resource_info, course_infos)

    # populate the other activity files
    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/inforef.xml", mode='w', buffering=-1, encoding=None)
    inforef = ET.Element("inforef")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/inforef.xml", inforef)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/roles.xml", mode='w', buffering=-1, encoding=None)
    roles = ET.Element("roles")
    role_overrides = ET.SubElement(roles, "role_overrides")
    role_assignments = ET.SubElement(roles, "role_assignments")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/roles.xml", roles)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/grades.xml", mode='w', buffering=-1, encoding=None)
    grades = ET.Element("activity_gradebook")
    ET.SubElement(grades, "grade_items")
    ET.SubElement(grades, "grade_letters")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/grades.xml", grades)

    open(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/grade_history.xml", mode='w', buffering=-1, encoding=None)
    grade_history = ET.Element("grade_history")
    ET.SubElement(grades, "grade_grades")
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/grade_history.xml", grade_history)
    return ET


def mdl_modulefile(sec_id, activity_id, course_infos):
    module = ET.Element("module", id=activity_id, version="2018120300")
    ET.SubElement(module, "modulename").text = "url"
    ET.SubElement(module, "sectionid").text = sec_id
    ET.SubElement(module, "sectionnumber").text = '0'
    ET.SubElement(module, "idnumber").text = '1584886844'
    ET.SubElement(module, "score").text = '0'
    ET.SubElement(module, "indent").text = '0'
    ET.SubElement(module, "visible").text = '1'
    ET.SubElement(module, "visibleoncoursepage").text = '1'
    ET.SubElement(module, "visibleold").text = '1'
    ET.SubElement(module, "groupmode").text = '0'
    ET.SubElement(module, "groupingid").text = '0'
    ET.SubElement(module, "completion").text = '1'
    ET.SubElement(module, "completiongradeitemnumber").text = '$@NULL@$'
    ET.SubElement(module, "completionview").text = '0'
    ET.SubElement(module, "completionexpected").text = '0'
    ET.SubElement(module, "availability").text = '$@NULL@$'
    ET.SubElement(module, "showdescription").text = '1'
    ET.SubElement(module, "tags").text = ''
    writetoxml_update_needed_mdl_header(
                                        f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/module.xml",
                                        module)


def mdl_activityfile(sec_id, activity_id, resource_info, course_infos):
    activity = ET.Element("activity", id="9", moduleid=activity_id, modulename="url", contextid="81")
    url = ET.SubElement(activity, "url", id="9")
    ET.SubElement(url, "name").text = resource_info['title'] if resource_info['title'] != '' else resource_info['url']
    ET.SubElement(url, "intro").text = fill_activity_intro(resource_info)
    ET.SubElement(url, "introformat").text = '1'
    ET.SubElement(url, "externalurl").text = resource_info['url']
    ET.SubElement(url, "display").text = '1'
    ET.SubElement(url, "displayoptions").text = 'a:1:{s:10:"printintro";i:1;}'
    ET.SubElement(url, "parameters").text = 'a:0:{}'
    ET.SubElement(url, "timemodified").text = str(int(time.time()))
    writetoxml_update_needed_mdl_header(f"{generated_folder}/{course_infos['crs_bkp_name']}/activities/url_{activity_id}/url.xml", activity)


def fill_activity_intro(resource_info):
    intro = f"<div>{resource_info['description']}</div>"
    if resource_info['activity_descstyle'] == 'bullets':
        intro+= "<div><ul>"
        for key in resource_info.keys():
            if resource_info[key] != '':
                if key not in ['url', 'x5gon_id', 'material_id', 'title', 'images', 'thumnail_url', 'description', 'concepts', 'generated_activity_id', 'generated_section_id', 'activity_descstyle', 'order']:
                    intro+= "<li>"
                    intro+= f"<b>{key}</b>: {resource_info[key]}"
                    intro+= "</li>"
                if key == 'url':
                    intro+= "<li>"
                    intro+= f"<b>{key}</b>: <a href='{resource_info[key]}' target='_blank'>{resource_info[key]}</a>"
                    intro+= "</li>"
                if key == 'concepts' and resource_info[key] != []:
                    intro+= "<li>"
                    intro+= f"<b>{key}</b>: {fill_concepts_list(resource_info[key])}"
                    intro+= "</li>"
        intro+= "</ul></div>"
    if resource_info['activity_descstyle'] == 'table':
        intro+= "<div><table><caption></caption><tbody>"
        for key in resource_info.keys():
            if resource_info[key] != '':
                if key not in ['url', 'x5gon_id', 'material_id', 'title', 'images', 'thumnail_url', 'description', 'generated_activity_id', 'generated_section_id', 'activity_descstyle', 'concepts', 'order']:
                    intro+= "<tr>"
                    intro+= f"<th scope='row'>{key}</th><td> {resource_info[key]}</td>"
                    intro+= "</tr>"
                if key == 'url':
                    intro+= "<tr>"
                    intro+= f"<th scope='row'>{key}</th><td> <a href='{resource_info[key]}' target='_blank'>{resource_info[key]}</a></td>"
                    intro+= "</tr>"
                if key == 'concepts' and resource_info[key] != []:
                    intro+= "<tr>"
                    intro+= f"<th scope='row'>{key}</th>"
                    intro+= f"<td> {fill_concepts_list(resource_info[key])}</td>"
                    intro+= "</tr>"
        intro+= "</tbody></table></div>"
    return intro


def fill_concepts_list(concepts):
    concepts_style = [f"<a href='{concept['url']}' target='_blank'>{concept['label']}</a>" for concept in concepts]
    return ', '.join(concepts_style)
