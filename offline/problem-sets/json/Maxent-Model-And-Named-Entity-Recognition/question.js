var __c2g_questions={"metadata":{"title":"Maxent Model and Named Entity Recognition","open_time":"2012-03-31 0001","soft_close_time":"2012-04-17 2359","hard_close_time":"2012-05-22 2359","duration":"0","retry_delay":"10","maximum_submissions":"5","modified_time":"1335393991259","parameters":{"show_explanations":{"question":"after_hard_close_time","option":"before_soft_close_time","score":"before_soft_close_time"}},"maximum_score":"5"},"preamble":{},"data":{"question_groups":{"question_group":[{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"e11995d54691c8f2e0a9edb6bcec5edc","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We surveyed cancer types from 569 patients in a cancer hospital and found the gender distribution of patients who have and don't have hodgkins lymphoma. What is the joint probability P(female, lymphoma) and conditional probability P(female|lymphoma)?\n<br \/><br \/><br \/>\n<table><tr><td><\/td><td>Lymphoma<\/td><td>No Lymphoma<\/td><\/tr>\n<tr><td>Male<\/td><td>59<\/td><td>230<\/td><\/tr>\n<tr><td>Female<\/td><td>10<\/td><td>270<\/td><\/tr>\n<\/table>","explanation":"$$P(female, lymphoma) = \\frac{10}{569} = 0.018$$<br \/><br \/>\n$$P(female | lymphoma) = \\frac{10}{59 + 10} = 0.145$$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"ab8a821e1035425caf4deb412fc64f6c","selected_score":"1","unselected_score":"0"},"text":"0.018, 0.145","explanation":"Correct!"},{"@attributes":{"id":"e9c60d6828c14053f8bc83253eee9005","selected_score":"0","unselected_score":"0"},"text":"0.104, 0.855","explanation":"Make sure that you have the right numerators for both probabilities."},{"@attributes":{"id":"e7cfc86728417ea534fae17e3ef057d9","selected_score":"0","unselected_score":"0"},"text":"0.018, 0.036","explanation":"The denominator for the conditional probability is the number of people who have lymphoma"},{"@attributes":{"id":"d7d5a7c71c2318a0a54617fdb3b77703","selected_score":"0","unselected_score":"0"},"text":"0.036, 0.145","explanation":"The denominator for the joint probability is the total number of patients"}]}}}},{"@attributes":{"id":"81c61432eed870946199dbec8bab9c53","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We surveyed cancer types from 502 patients in a cancer hospital and found the gender distribution of patients who have and don't have hodgkins lymphoma. What is the joint probability P(female, lymphoma) and conditional probability P(female|lymphoma)?\n<br \/><br \/><br \/>\n<table><tr><td><\/td><td>Lymphoma<\/td><td>No Lymphoma<\/td><\/tr>\n<tr><td>Male<\/td><td>52<\/td><td>200<\/td><\/tr>\n<tr><td>Female<\/td><td>10<\/td><td>240<\/td><\/tr>\n<\/table>","explanation":"$$P(female, lymphoma) = \\frac{10}{502} = 0.020$$<br \/><br \/>\n$$P(female | lymphoma) = \\frac{10}{52 + 10} = 0.161$$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"29e26db01cb25f77978a04ccd88b0c1f","selected_score":"1","unselected_score":"0"},"text":"0.020, 0.161","explanation":"Correct!"},{"@attributes":{"id":"e26720ee1ac3079f734ac5f1c03b59b3","selected_score":"0","unselected_score":"0"},"text":"0.104, 0.839","explanation":"Make sure that you have the right numerators for both probabilities."},{"@attributes":{"id":"0329638bdcf60e392db6d8af9fca16cb","selected_score":"0","unselected_score":"0"},"text":"0.020, 0.040","explanation":"The denominator for the conditional probability is the number of people who have lymphoma"},{"@attributes":{"id":"4f61773f5ae0225d0c1ab8473bc96516","selected_score":"0","unselected_score":"0"},"text":"0.040, 0.161","explanation":"The denominator for the joint probability is the total number of patients"}]}}}},{"@attributes":{"id":"826d796fb5c63d9f39f4023daaf7cf15","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"We surveyed cancer types from 266 patients in a cancer hospital and found the gender distribution of patients who have and don't have hodgkins lymphoma. What is the joint probability P(female, lymphoma) and conditional probability P(female|lymphoma)?\n<br \/><br \/><br \/>\n<table><tr><td><\/td><td>Lymphoma<\/td><td>No Lymphoma<\/td><\/tr>\n<tr><td>Male<\/td><td>26<\/td><td>100<\/td><\/tr>\n<tr><td>Female<\/td><td>10<\/td><td>130<\/td><\/tr>\n<\/table>","explanation":"$$P(female, lymphoma) = \\frac{10}{266} = 0.038$$<br \/><br \/>\n$$P(female | lymphoma) = \\frac{10}{26 + 10} = 0.278$$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"c7cf1760bda1945154cbc1a3142f3023","selected_score":"1","unselected_score":"0"},"text":"0.038, 0.278","explanation":"Correct!"},{"@attributes":{"id":"78170b98ee93d8fdacb00cc2b57c463a","selected_score":"0","unselected_score":"0"},"text":"0.098, 0.722","explanation":"Make sure that you have the right numerators for both probabilities."},{"@attributes":{"id":"7f51cc90a7dfd0483c61523f8f1f0f3f","selected_score":"0","unselected_score":"0"},"text":"0.038, 0.071","explanation":"The denominator for the conditional probability is the number of people who have lymphoma"},{"@attributes":{"id":"fbba377814dfd44ce8523ae295730ef4","selected_score":"0","unselected_score":"0"},"text":"0.071, 0.278","explanation":"The denominator for the joint probability is the total number of patients"}]}}}}]},{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"418e72e34589f9ea2569c4063dc016d3","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"In the maxent model, we've learned that P(c|d,&lambda;) = exp&Sigma;&lambda;<sub>i<\/sub>f<sub>i<\/sub>(c,d)\/&Sigma;exp&Sigma;&lambda;<sub>i<\/sub>f<sub>i<\/sub>(c',d). This equation is also in the lecture slide #25. Given the 3 classes and the 3 features, compute the following probabilities. w<sub>i<\/sub>  = \"Go\u00e9ric\" <br \/><br \/>\n<ul>\n<li>P(PERSON | by Go\u00e9ric) = <\/li>\n<li>P(LOCATION | by Go\u00e9ric) = <\/li>\n<li>P(DRUG | by Go\u00e9ric) = <\/li>\n<\/ul><br\/>\n<table><tr><td>Weight<\/td><td>Feature<\/td><\/tr>\n<tr><td>&nbsp;1.8<\/td><td>f<sub>1<\/sub>(c, d) = [c = LOCATION & w<sub>i-1<\/sub> = in & isCapitalized(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>-0.6<\/td><td>f<sub>2<\/sub>(c, d) = [c = LOCATION & hasAccentedLatinChar(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>&nbsp;0.3<\/td><td>f<sub>3<\/sub>(c, d) = [c = DRUG & ends(w<sub>i<\/sub>, c)]<\/td><\/tr>\n<\/table>\n&nbsp;&nbsp;","explanation":"<ul>\n<li>P(PERSON | by Go\u00e9ric) = e<sup>0<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.6<\/sup> + e<sup>0.3<\/sup>)  = 0.34<\/li>\n<li>P(LOCATION | by Go\u00e9ric) = e<sup>-0.6<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.6<\/sup> + e<sup>0.3<\/sup>) = 0.19<\/li>\n<li>P(DRUG | by Go\u00e9ric) = e<sup>0.3<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.6<\/sup> + e<sup>0.3<\/sup>) = 0.47 <\/li>\n<\/ul>","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"0fc9130d7ba2b11c018aa14f68bb2789","selected_score":"1","unselected_score":"0"},"text":"0.34, 0.19, 0.47","explanation":"Correct!"},{"@attributes":{"id":"2b9a37fd74b230ea2726df24f7d6307c","selected_score":"0","unselected_score":"0"},"text":"0.18, 0.59, 0.24","explanation":"f<sub>1<\/sub> must not be counted towards P(LOCATION | by Go\u00e9ric) because Go\u00e9ric is not preceded by \"in\"."},{"@attributes":{"id":"42262855fd0adade6c539d3ef356a30e","selected_score":"0","unselected_score":"0"},"text":"0.44, 0.24, 0.32","explanation":"f<sub>2<\/sub> must be only counted towards the class LOCATION due to its condition, c = LOCATION."},{"@attributes":{"id":"81938347c1415c2be9403f2c3125ecec","selected_score":"0","unselected_score":"0"},"text":"0.10, 0.06, 0.84","explanation":"f<sub>1<\/sub> must not be counted towards P(DRUG| by Go\u00e9ric) because Go\u00e9ric is not preceded by \"in\"."}]}}}},{"@attributes":{"id":"d02eb25a097293cd0fd92c08ade6427e","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"In the maxent model, we've learned that P(c|d,&lambda;) = exp&Sigma;&lambda;<sub>i<\/sub>f<sub>i<\/sub>(c,d)\/&Sigma;exp&Sigma;&lambda;<sub>i<\/sub>f<sub>i<\/sub>(c',d). This equation is also in the lecture slide #25. Given the 3 classes and the 3 features, compute the following probabilities. w<sub>i<\/sub>  = \"Go\u00e9ric\" <br \/><br \/>\n<ul>\n<li>P(PERSON | by Go\u00e9ric) = <\/li>\n<li>P(LOCATION | by Go\u00e9ric) = <\/li>\n<li>P(DRUG | by Go\u00e9ric) = <\/li>\n<\/ul><br\/>\n<table><tr><td>Weight<\/td><td>Feature<\/td><\/tr>\n<tr><td>&nbsp;1.2<\/td><td>f<sub>1<\/sub>(c, d) = [c = LOCATION & w<sub>i-1<\/sub> = in & isCapitalized(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>-0.3<\/td><td>f<sub>2<\/sub>(c, d) = [c = LOCATION & hasAccentedLatinChar(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>&nbsp;0.4<\/td><td>f<sub>3<\/sub>(c, d) = [c = DRUG & ends(w<sub>i<\/sub>, c)]<\/td><\/tr>\n<\/table>\n&nbsp;&nbsp;","explanation":"<ul>\n<li>P(PERSON | by Go\u00e9ric) = e<sup>0<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.3<\/sup> + e<sup>0.4<\/sup>)  = 0.31<\/li>\n<li>P(LOCATION | by Go\u00e9ric) = e<sup>-0.3<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.3<\/sup> + e<sup>0.4<\/sup>) = 0.23<\/li>\n<li>P(DRUG | by Go\u00e9ric) = e<sup>0.4<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.3<\/sup> + e<sup>0.4<\/sup>) = 0.46 <\/li>\n<\/ul>","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"3d5776f9da7f55747a9c0e47de66a3cf","selected_score":"1","unselected_score":"0"},"text":"0.31, 0.23, 0.46","explanation":"Correct!"},{"@attributes":{"id":"dbd27f209019f0f9a864b318998b8c12","selected_score":"0","unselected_score":"0"},"text":"0.20, 0.50, 0.30","explanation":"f<sub>1<\/sub> must not be counted towards P(LOCATION | by Go\u00e9ric) because Go\u00e9ric is not preceded by \"in\"."},{"@attributes":{"id":"42760f00ce2a84680e7aa66fe59517db","selected_score":"0","unselected_score":"0"},"text":"0.35, 0.26, 0.39","explanation":"f<sub>2<\/sub> must be only counted towards the class LOCATION due to its condition, c = LOCATION."},{"@attributes":{"id":"ae44ae8dd7cee6c1de7baff05389fe48","selected_score":"0","unselected_score":"0"},"text":"0.15, 0.11, 0.74","explanation":"f<sub>1<\/sub> must not be counted towards P(DRUG| by Go\u00e9ric) because Go\u00e9ric is not preceded by \"in\"."}]}}}},{"@attributes":{"id":"c28298f9f4491b8b14c5d65f4428b2f2","type":"GS_Choice_Answer_Question"},"metadata":{"parameters":{"rescale_score":"1","choice_type":"radio"}},"data":{"text":"In the maxent model, we've learned that P(c|d,&lambda;) = exp&Sigma;&lambda;<sub>i<\/sub>f<sub>i<\/sub>(c,d)\/&Sigma;exp&Sigma;&lambda;<sub>i<\/sub>f<sub>i<\/sub>(c',d). This equation is also in the lecture slide #25. Given the 3 classes and the 3 features, compute the following probabilities. w<sub>i<\/sub>  = \"Go\u00e9ric\" <br \/><br \/>\n<ul>\n<li>P(PERSON | by Go\u00e9ric) = <\/li>\n<li>P(LOCATION | by Go\u00e9ric) = <\/li>\n<li>P(DRUG | by Go\u00e9ric) = <\/li>\n<\/ul><br\/>\n<table><tr><td>Weight<\/td><td>Feature<\/td><\/tr>\n<tr><td>&nbsp;1.5<\/td><td>f<sub>1<\/sub>(c, d) = [c = LOCATION & w<sub>i-1<\/sub> = in & isCapitalized(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>-0.5<\/td><td>f<sub>2<\/sub>(c, d) = [c = LOCATION & hasAccentedLatinChar(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>&nbsp;0.7<\/td><td>f<sub>3<\/sub>(c, d) = [c = DRUG & ends(w<sub>i<\/sub>, c)]<\/td><\/tr>\n<\/table>\n&nbsp;&nbsp;","explanation":"<ul>\n<li>P(PERSON | by Go\u00e9ric) = e<sup>0<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.5<\/sup> + e<sup>0.7<\/sup>)  = 0.28<\/li>\n<li>P(LOCATION | by Go\u00e9ric) = e<sup>-0.5<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.5<\/sup> + e<sup>0.7<\/sup>) = 0.17<\/li>\n<li>P(DRUG | by Go\u00e9ric) = e<sup>0.7<\/sup> \/ (e<sup>0<\/sup> + e<sup>-0.5<\/sup> + e<sup>0.7<\/sup>) = 0.56 <\/li>\n<\/ul>","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":[{"@attributes":{"id":"be3b57b2fe9388e3aca55fd637fdd0ac","selected_score":"1","unselected_score":"0"},"text":"0.28, 0.17, 0.56","explanation":"Correct!"},{"@attributes":{"id":"71aa9246cb9749625d8261e9f59d58e9","selected_score":"0","unselected_score":"0"},"text":"0.17, 0.47, 0.35","explanation":"f<sub>1<\/sub> must not be counted towards P(LOCATION | by Go\u00e9ric) because Go\u00e9ric is not preceded by \"in\"."},{"@attributes":{"id":"5570ed7fbbce09e51d59f9d66fe2d433","selected_score":"0","unselected_score":"0"},"text":"0.35, 0.21, 0.43","explanation":"f<sub>2<\/sub> must be only counted towards the class LOCATION due to its condition, c = LOCATION."},{"@attributes":{"id":"52cc41735714cbe353edaeaeeea5f8e3","selected_score":"0","unselected_score":"0"},"text":"0.09, 0.06, 0.85","explanation":"f<sub>1<\/sub> must not be counted towards P(DRUG| by Go\u00e9ric) because Go\u00e9ric is not preceded by \"in\"."}]}}}}]},{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"5337c6dc0e4aa1a3fe866ea59d24235e","type":"GS_Short_Answer_Question_Simple"},"metadata":{"parameters":{"rescale_score":"1","type":"numeric"}},"data":{"text":"We have defined three classes {PERSON, LOCATION, other} and five features like the following. We have also hand-labeled a sentence to train a NER classifier. Each word is labeled in the format of {word}\/{class} (e.g. Obama\/PER). Compute the sum of the empirical expectations of all features for the following sentence. The empirical expectation of a feature is $$ \\Sigma_{(c,d)\\in observed(C,D)} f_i(c,d)$$\n<br \/><br \/>\n<i>President\/O Obama\/PER met\/O with\/O former\/O President\/O George\/PER H.W.\/PER Bush\/PER and\/O former\/O Florida\/LOC Gov.\/O Jeb\/PER Bush\/PER in\/O the\/O Oval\/LOC Office\/LOC on\/O Friday,\/O joining\/O in\/O a\/O bipartisan\/O gathering\/O in\/O an\/O election\/O year.\/O <\/i>\n<br\/><br\/>\n<table><tr><td>Features<\/td><\/tr>\n<tr><td>f<sub>1<\/sub>(c, d) = [c = LOCATION & isCapitalized(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>f<sub>2<\/sub>(c, d) = [c = LOCATION & classOf(w<sub>i-1<\/sub>) = LOCATION]<\/td><\/tr>\n<tr><td>f<sub>3<\/sub>(c, d) = [c = PERSON & isCapitalized(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>f<sub>4<\/sub>(c, d) = [c = PERSON & classOf(w<sub>i-1<\/sub>) = PERSON]<\/td><\/tr>\n<tr><td>f<sub>5<\/sub>(c, d) = [c = PERSON & w<sub>i-1<\/sub> = \"President\" ]<\/td><\/tr>\n<\/table>","explanation":"See the slide #14-17 <br\/><br\/>\n $$empirical E(f_1) =  3 $$<br\/><br\/>\n $$empirical E(f_2) =  1 $$<br\/><br\/>\n $$empirical E(f_3) =  6 $$<br\/><br\/>\n $$empirical E(f_4) =  3 $$<br\/><br\/>\n $$empirical E(f_5) =  2 $$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":{"@attributes":{"id":"f11f2207d2d6e615d707cbe8ad52899a","selected_score":"1","unselected_score":"0"},"text":"15","explanation":"Correct!"}}}}},{"@attributes":{"id":"152cf0d955e0b29085407be8686a7b52","type":"GS_Short_Answer_Question_Simple"},"metadata":{"parameters":{"rescale_score":"1","type":"numeric"}},"data":{"text":"We have defined three classes {PERSON, LOCATION, other} and five features like the following. We have also hand-labeled a sentence to train a NER classifier. Each word is labeled in the format of {word}\/{class} (e.g. Obama\/PER). Compute the sum of the empirical expectations of all features for the following sentence. The empirical expectation of a feature is $$ \\Sigma_{(c,d)\\in observed(C,D)} f_i(c,d)$$\n<br \/><br \/>\n<i>President\/O Obama\/PER met\/O with\/O former\/O President\/O George\/PER H.W.\/PER Bush\/PER and\/O former\/O Florida\/LOC Gov.\/O Jeb\/PER Bush\/PER in\/O the\/O Oval\/LOC Office\/LOC on\/O Friday,\/O joining\/O in\/O a\/O bipartisan\/O gathering\/O in\/O an\/O election\/O year.\/O <\/i>\n<br\/><br\/>\n<table><tr><td>Features<\/td><\/tr>\n<tr><td>f<sub>1<\/sub>(c, d) = [c = LOCATION & isCapitalized(w<sub>i<\/sub>)]<\/td><\/tr>\n<tr><td>f<sub>2<\/sub>(c, d) = [c = LOCATION & classOf(w<sub>i-1<\/sub>) = LOCATION]<\/td><\/tr>\n<tr><td>f<sub>3<\/sub>(c, d) = [c = PERSON & w<sub>i-1<\/sub> = \"Gov.\"]<\/td><\/tr>\n<tr><td>f<sub>4<\/sub>(c, d) = [c = PERSON & w<sub>i-1<\/sub> = \"President\"]<\/td><\/tr>\n<tr><td>f<sub>5<\/sub>(c, d) = [c = PERSON & isCapitalized(w<sub>i<\/sub>) ]<\/td><\/tr>\n<\/table>","explanation":"See the slide #14-17 <br\/><br\/>\n $$empirical E(f_1) =  3 $$<br\/><br\/>\n $$empirical E(f_2) =  1 $$<br\/><br\/>\n $$empirical E(f_3) =  1 $$<br\/><br\/>\n $$empirical E(f_4) =  2 $$<br\/><br\/>\n $$empirical E(f_5) =  6 $$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":{"@attributes":{"id":"777de336e9fea819eec2106d8ab4ddc2","selected_score":"1","unselected_score":"0"},"text":"13","explanation":"Correct!"}}}}}]},{"@attributes":{"select":"1"},"preamble":{},"question":[{"@attributes":{"id":"0d99d2d3832e1d2e5e9f4285e9083946","type":"GS_Short_Answer_Question_Simple"},"metadata":{"parameters":{"rescale_score":"1","type":"numeric"}},"data":{"text":"We've built an NER system and ran it on a tiny dataset. Based on the following result, compute the F1 score of the system. (round to the 3 decimal places, e.g. 0.123)\n<br\/><br \/>\n<table>\n<tr><td><\/td><td>GOLD PERSON<\/td><td>GOLD other<\/td><\/tr>\n<tr><td>SYSTEM GUESS PERSON<\/td><td>20<\/td><td>33<\/td><\/tr>\n<tr><td>SYSTEM GUESS other<\/td><td>10<\/td><td>4<\/td><\/tr>","explanation":"Precision: % of selected items that are correct<br\/>\nRecall: % of correct items that are selected<br\/>\nF<sub>1<\/sub>: 2PR\/(P+R)<br\/>\n<br\/>\nPrecision: 20 \/ 53 = 0.377<br\/>\nRecall: 20 \/ 30 = 0.667<br\/>\nF<sub>1<\/sub>: (2 * 0.377 * 0.677) \/ (0.377 + 0.677) = 0.482","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":{"@attributes":{"id":"25afcead9814d8e8c33447289c2d1894","selected_score":"1","unselected_score":"0"},"text":"0.482","explanation":"Correct!"}}}}},{"@attributes":{"id":"71ec1f32a6eaad7c17683a435e43218e","type":"GS_Short_Answer_Question_Simple"},"metadata":{"parameters":{"rescale_score":"1","type":"numeric"}},"data":{"text":"We've built an NER system and ran it on a tiny dataset. Based on the following result, compute the F1 score of the system. (round to the 3 decimal places, e.g. 0.123)\n<br\/><br \/>\n<table>\n<tr><td><\/td><td>GOLD PERSON<\/td><td>GOLD other<\/td><\/tr>\n<tr><td>SYSTEM GUESS PERSON<\/td><td>15<\/td><td>4<\/td><\/tr>\n<tr><td>SYSTEM GUESS other<\/td><td>18<\/td><td>6<\/td><\/tr>","explanation":"Precision: % of selected items that are correct<br\/>\nRecall: % of correct items that are selected<br\/>\nF<sub>1<\/sub>: 2PR\/(P+R)<br\/>\n<br\/>\nPrecision: 15 \/ 19 = 0.789<br\/>\nRecall: 15 \/ 33 = 0.455<br\/>\nF<sub>1<\/sub>: (2 * 0.789 * 0.455) \/ (0.789 + 0.455) = 0.577","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":{"@attributes":{"id":"9d9b733bdb2575a4bbc383ae5b229094","selected_score":"1","unselected_score":"0"},"text":"0.577","explanation":"Correct!"}}}}},{"@attributes":{"id":"f0658b6495b0c862dfca37f6aa509570","type":"GS_Short_Answer_Question_Simple"},"metadata":{"parameters":{"rescale_score":"1","type":"numeric"}},"data":{"text":"We've built an NER system and ran it on a tiny dataset. Based on the following result, compute the F1 score of the system. (round to the 3 decimal places, e.g. 0.123)\n<br\/><br \/>\n<table>\n<tr><td><\/td><td>GOLD PERSON<\/td><td>GOLD other<\/td><\/tr>\n<tr><td>SYSTEM GUESS PERSON<\/td><td>20<\/td><td>10<\/td><\/tr>\n<tr><td>SYSTEM GUESS other<\/td><td>11<\/td><td>14<\/td><\/tr>","explanation":"Precision: % of selected items that are correct<br\/>\nRecall: % of correct items that are selected<br\/>\nF<sub>1<\/sub>: 2PR\/(P+R)<br\/>\n<br\/>\nPrecision: 20 \/ 30 = 0.667<br\/>\nRecall: 20 \/ 31 = 0.645<br\/>\nF<sub>1<\/sub>: (2 * 0.667 * 0.645) \/ (0.667 + 0.645) = 0.656","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":{"@attributes":{"id":"a5816f68fe9e55021bb7937356f4f68b","selected_score":"1","unselected_score":"0"},"text":"0.656","explanation":"Correct!"}}}}}]},{"@attributes":{"select":"1"},"preamble":{},"question":{"@attributes":{"id":"9337a247d6767a488a275205c9d111f5","type":"GS_Short_Answer_Question_Simple"},"metadata":{"parameters":{"rescale_score":"1","type":"numeric"}},"data":{"text":"Suppose we build a maxent classifier over 5 classes {PERSON, ORGANIZATION, LOCATION, PRODUCT, OTHER}. Suppose further that for a particular data item, one feature matches for the class PERSON with its lambda weight as $$\\ln4$$. No other features match that particular data item for any other class. What will be the probability of the class PERSON on this data item at classification time? (numerical response rounded to the nearest tenths, e.g. 0.1 or 0.9)","explanation":"For the particular data item, the vote for the class PERSON is ln4 and the votes for the other classes are 0. Thus, the probability of the class PERSON on this data item is like the following:  <br \/><br \/>\n\n$$\\frac{e^{ln4}}{e^{ln4}+e^{0}+e^{0}+e^{0}+e^{0}} = \\frac{4}{4+1+1+1+1}  = 0.5$$","option_groups":{"@attributes":{"randomize":"true"},"option_group":{"@attributes":{"select":"all"},"option":{"@attributes":{"id":"872671bcc8b0acdc16e71638a1b2060d","selected_score":"1","unselected_score":"0"},"text":"0.5","explanation":"Correct!"}}}}}}]}}};renderQuiz(__c2g_questions);