// This repository is attached to the paper: "GoSeed: Generating an Optimal Seeding Plan for Deduplicated Storage".
// Authors: Aviv Nachman, Gala Yadgar and Sarai Sheinvald.
// Conference: FAST20, 18th USENIX Conference on File and Storage Technologies.
// Link: https://www.usenix.org/conference/fast20/presentation/nachman

#include "gurobi_c++.h"
#include <fstream>
#include <chrono>
#include <set>
#include <boost/algorithm/string.hpp>
#include <unordered_map> 

#define UNDEFINED_STRING "-1"
#define UNDEFINED_DOUBLE -1.0
#define UNDEFINED_INT -1
#define UNDEFINED_STATUS "UNDEFINED_STATUS"

std::string depth_level = UNDEFINED_STRING;          //File system depth.
std::string v1_file_system_start = UNDEFINED_STRING;    //ID of the first file system.
std::string v2_file_system_end = UNDEFINED_STRING;      //ID of the last file system.
int average_block_size = UNDEFINED_INT;              //Average block size in the system (corresponding to rabin fingerprint)
double T_percentage = UNDEFINED_DOUBLE;              //The % we want to migrate to an empty destination.
double MM_percentage = UNDEFINED_DOUBLE;             //The tolerance we can afford in the migration.
std::string input_file_name = UNDEFINED_STRING;      //Name of the input file, contains all the information needed.
std::string volume_list = UNDEFINED_STRING;      //Name of the input file, contains all the information needed.
std::string benchmarks_file_name = UNDEFINED_STRING; //File we save our benchmarks, every line will be a different migration plan summary.
double model_time_limit = UNDEFINED_DOUBLE;          //Time limit for the solver.
bool time_limit_option = false;                      //Do we restrict the solver in time limit? (True if model_time_limit is greater than 0).
double T_Kbytes = UNDEFINED_DOUBLE;                  //KB we desire to migrate.
double epsilon_Kbytes = UNDEFINED_DOUBLE;            //KB we can tolerate.
double Kbytes_to_replicate = UNDEFINED_DOUBLE;       //KB to replicated as a result from the migration plan.
long int num_of_blocks = UNDEFINED_INT;              //Number of blocks in the input file
double actual_M_percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to migrate.
double actual_M_Kbytes = UNDEFINED_DOUBLE;           //Number of containers we decided to migrate.
double actual_R_percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to repicate.
double actual_traffic_Percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to repicate.
double actual_volume_clean_percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to repicate.
double actual_volume_add_percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to repicate.
double actual_volume_change_percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to repicate.
double total_traffic_and_clean_percentage = UNDEFINED_DOUBLE;         //The % of physical containers we decided to repicate.
double actual_R_Kbytes = UNDEFINED_DOUBLE;           //Number of containers we decided to repicate.
int num_of_files = UNDEFINED_INT;                    //Number of files in our input.
std::string seed = UNDEFINED_STRING;                 //Seed for the solver.
std::string number_of_threads = UNDEFINED_STRING;    //Number of threads we restrict our solver to run with.
std::string solution_status = UNDEFINED_STATUS;      //Solver status at the end of the optimization.
int filter_factor = UNDEFINED_INT;                   // if filter heuristic was applied, k determines the number of following zeros.
double total_block_size_Kbytes = 0;                  //the total physical size of the system in KB units.
std::string input_file_name_v2 = UNDEFINED_STRING;   //Name of the input file of second volume, contains all the information needed.
int variable_number = UNDEFINED_INT;
int constraint_number = UNDEFINED_INT;
int source_block_number = UNDEFINED_INT;
int target_block_number = UNDEFINED_INT;
int intersect_block_number = UNDEFINED_INT;

/**
 * @brief counts the number of metadata lines in the input file.
 * metadata line is defined to have # symbol at the start of the line.
 * 
 * @param input_file_name the input file name.
 * @return int number of metadata lines in the input file
 */
int get_num_of_metadata_lines(std::string &input_file_name)
{
    std::ifstream f(input_file_name.c_str(), std::ifstream::in);
    int counter = 0;
    std::string content;
    if (!f.is_open())
    {
        std::cout << "error opening file: " << input_file_name << std::endl;
        exit(1);
    }
    std::getline(f, content);
    while (content[0] == '#')
    {
        counter++;
        std::getline(f, content);
    }
    f.close();
    return counter;
}

/**
 * @brief Retrieves the number of files and containers in the input.
 * metadata lines are in format: "# <type_of_information>:<value>"
 * @param f reference to the input stream
 * @param num_of_metadata_lines the number of metadata lines
 */
std::pair<int, int> get_num_of_blocks_and_files(std::string f, int num_of_metadata_lines)
{
    std::ifstream f_stream(f.c_str(), std::ifstream::in);
    if (!f_stream.is_open())
    {
        std::cout << "error opening volume file - get_num_of_blocks_and_files" << f << std::endl;
        exit(1);
    }

    const std::string type_of_info_file = "# Num files";
    const std::string type_of_info_block = "# Num Blocks";
    std::string content;
    std::string number_as_string;
    std::string type_of_info;
    bool set_num_files = false, set_num_blocks = false;

    for (int i = 0; i < num_of_metadata_lines; i++)
    {
        std::getline(f_stream, content);
        type_of_info = content.substr(0, content.find(": "));
        if (type_of_info == type_of_info_file)
        {
            num_of_files = std::stoi(content.substr(2 + content.find(": "))); //sets global variable
            set_num_files = true;
        }
        if (type_of_info == type_of_info_block)
        {
            num_of_blocks = std::stol(content.substr(2 + content.find(": "))); //sets global variable
            source_block_number = num_of_blocks;
            set_num_blocks = true;
        }
    }
    if (!set_num_blocks || !set_num_files)
    {
        std::cout << "cannot retrieve number of files or number of blocks from the input" << std::endl;
        exit(1);
    }
    f_stream.close();
    return std::make_pair(num_of_blocks, num_of_files);
}


/**
 * @brief Splits str according to delimiter, the result strings are stored in a std::vector.
 * 
 * @param str std::string to split.
 * @param delimiter split according to delimiter.
 * @return std::vector<std::string> the splitted std::string in a std::vector.
 */
std::vector<std::string> split_string(std::string str, const std::string &delimiter)
{
    std::vector<std::string> result;
    boost::split(result, str, boost::is_any_of(delimiter));
    return result;
}

void put_v2_in_hash_table(std::ifstream &fv2, std::unordered_map<std::string, int> &hashmap) {
    target_block_number = 0;
    std::string content;
    while (std::getline(fv2, content)) {
        std::vector<std::string> splitLine = split_string(content, ",");
        if(splitLine[0] == "B") {
            target_block_number++;
            hashmap[splitLine[2]] = std::stoi(splitLine[1]);
        }
    }
 
}

/**
 * @brief Computes the actual migration, also save the serial number of the files chosen in the migration plan.
 * print_to files will contain all the serial numbers of the files chosen to move in the migration plan (seperated by new line).
 * @param containers_migrated Assigned ILP variables for the containers to migrate.
 * @param files Assigned ILP variables for the files that move/stay.
 * @param print_to Output file for the files to move.
 */
void calculate_migration_and_save_solution(GRBVar *blocks_migrated, GRBVar *blocks_replicated, std::vector<bool> blocks_is_in_intersect, GRBVar *files, std::string print_to, double *block_size)
{
    std::ofstream solution(print_to, std::ios_base::app);
    if (!solution)
    {
        std::cout << "Cannot open output file" << print_to << std::endl;
        exit(1);
    }
    solution << "this is the list of the files we should move:" << std::endl;
    for (int i = 0; i < num_of_files; i++)
    {
        if (files[i].get(GRB_DoubleAttr_X) != 0.0) //file is moved
        {
            solution << i << std::endl;
        }
    }
    double total_blocksMigrated = 0.0;
    double total_blocksReplicated = 0.0;
    double total_traffic = 0.0;
    double total_volume_change_add = 0.0;
    double total_volume_change_clean = 0.0;

    //Sum KB of the migrated blocks.
    for (long int i = 0; i < num_of_blocks; i++)
    {
        if (blocks_migrated[i].get(GRB_DoubleAttr_X) != 0.0)
        {
            total_blocksMigrated += block_size[i];
            if (blocks_is_in_intersect[i]) {
                total_volume_change_clean += block_size[i];
            } else {
                total_traffic += block_size[i];
            }
        }
    }
    //Sum KB of the replicated blocks.
    for (long int i = 0; i < num_of_blocks; i++)
    {
        if (blocks_replicated[i].get(GRB_DoubleAttr_X) != 0.0)
        {
            total_blocksReplicated += block_size[i];
            if (blocks_is_in_intersect[i]) {
                ;
            } else {
                total_volume_change_add += block_size[i];
            }
        }
    }    
    actual_M_Kbytes = total_blocksMigrated;
    actual_R_Kbytes = total_blocksReplicated;

    actual_M_percentage = (actual_M_Kbytes / total_block_size_Kbytes) * 100.0;
    actual_R_percentage = (actual_R_Kbytes / total_block_size_Kbytes) * 100.0;
    actual_traffic_Percentage = (total_traffic  / total_block_size_Kbytes) * 100.0;
    actual_volume_clean_percentage = (total_volume_change_clean  / total_block_size_Kbytes) * 100.0;
    actual_volume_add_percentage = (total_volume_change_add  / total_block_size_Kbytes) * 100.0;
    actual_volume_change_percentage = ((total_volume_change_add - total_volume_change_clean) / total_block_size_Kbytes) * 100.0;
    total_traffic_and_clean_percentage = ((total_traffic + total_volume_change_clean) / total_block_size_Kbytes) * 100.0;
    solution << "migrated..." << std::endl;
    solution << "actual_M_percentage: " << actual_M_percentage << std::endl;
    solution << "replicated..." << std::endl;
    solution << "actual_R_percentage: " << actual_R_percentage << std::endl;
    solution << "traffic..." << std::endl;
    solution << "traffic_KBytes: " << total_traffic << std::endl;
    solution << "actual_traffic_Percentage: " << actual_traffic_Percentage << std::endl;
    solution << "volume_change..." << std::endl;
    solution << "actual_volume_clean: " << total_volume_change_clean << std::endl;
    solution << "actual_volume_clean_percentage: " << actual_volume_clean_percentage << std::endl;
    solution << "actual_volume_add_percentage: " << actual_volume_add_percentage << std::endl;
    solution << "actual_volume_change_Percentage: " << actual_volume_change_percentage << std::endl;
    solution << "traffic and clean" << std::endl;
    solution << "total_traffic_and_clean_percentage: " << total_traffic_and_clean_percentage << std::endl;
    solution << "____________________________________" << std::endl << std::endl;
    solution.close();
}


/**
 * @brief Appends to the benchmark summary file the statistics of migration plan with the hyper paramaters passed.
 * 
 * @param total_time The total time took for the program to run.
 * @param solver_time Only the optimization time.
 */
void save_statistics(double total_time, double solver_time)
{
    std::ofstream out(benchmarks_file_name, std::ios_base::app);
    if (!out)
    {
        std::cout << "Cannot open output file\n";
    }   
    std::string is_there_time_limit = (time_limit_option) ? "yes" : "no";
    
    std::string v1_fileName = input_file_name.substr(input_file_name.find_last_of("/\\") + 1);
    std::string tmp = v1_fileName.substr(0, v1_fileName.find_last_of("_"));
    int v1First = std::stoi(tmp.substr(tmp.find_last_of("_") + 1, 3));
    int v1last = std::stoi(v1_fileName.substr(v1_fileName.find_last_of("_") + 1, 3));
    int v1NumFiles = v1last - v1First + 1;

    std::string v2_fileName = input_file_name_v2.substr(input_file_name_v2.find_last_of("/\\") + 1);
    tmp = v2_fileName.substr(0, v2_fileName.find_last_of("_"));
    int v2First = std::stoi(tmp.substr(tmp.find_last_of("_") + 1, 3));
    int v2last = std::stoi(v2_fileName.substr(v2_fileName.find_last_of("_") + 1, 3));
    int v2NumFiles = v2last - v2First + 1;

    out << v1First << ", "
        << v1last << ", "
        << v1NumFiles << ", "
        << v2First << ", "
        << v2last << ", "
        << v2NumFiles << ", "
        << "B, "
        << depth_level << ", "
        << filter_factor << ", "
        << average_block_size << ", "
        << num_of_blocks << ", "
        << T_percentage << ", "
        << T_Kbytes << ", "
        << actual_M_percentage << ", "
        << actual_M_Kbytes << ", "
        << MM_percentage << ", "
        << epsilon_Kbytes << ", "

        << (((double)actual_R_percentage) / 100 ) * ((double)total_block_size_Kbytes) << ", "
        << actual_R_percentage << ", "        
        << actual_traffic_Percentage << ", "
        << (((double)actual_traffic_Percentage) / 100 ) * ((double)total_block_size_Kbytes) << ", "
        << actual_volume_change_percentage << ", "
        << (((double)actual_volume_change_percentage) / 100 ) * ((double)total_block_size_Kbytes) << ", "

        << seed << ", "
        << number_of_threads << ", "
        << is_there_time_limit << ", "
        << solution_status << ", "
        << total_time << ", "
        << solver_time << ", "
        << total_time - solver_time  << ", "

        << variable_number << ", "
        << constraint_number << ", "
        << source_block_number << ", "
        << target_block_number << ", "
        << intersect_block_number << ", "

        << std::endl;
    out.close();
}

/**
 * @brief Saves to the disk the block_size array 
 * 
 * @param block_size contains the information of each block size in the systems
 */
void save_block_size_array(double *block_size)
{
    std::ofstream out("block_size.txt");
    if (!out)
    {
        std::cout << "Cannot open output file\n";
        return;
    }
    for (int i = 0; i < num_of_blocks; i++)
    {
        out << block_size[i] << std::endl;
    }
    out.close();
}

/**
 * @brief Reads from the disk the block_size array 
 * 
 * @param block_size contains the information of each block size in the systems
 */
void load_block_size_array_and_del_temp_file(double *block_size)
{
    std::ifstream in("block_size.txt");
    if (!in)
    {
        std::cout << "Cannot open input file\n";
        return;
    }
    for (int i = 0; i < num_of_blocks; i++)
    {
        in >> block_size[i];
    }
    in.close();

    if (remove("block_size.txt") != 0) // delete temp file
        std::cout << "Error deleting file" << std::endl;
}

std::vector<int> calcVolumeIntersect(std::string i_volume, std::string j_volume) 
{
    std::ifstream i_volume_stream(i_volume.c_str(), std::ifstream::in);
    if (!i_volume_stream.is_open())
    {
        std::cout << "error opening volume file - calcVolumeIntersect" << i_volume << std::endl;
        exit(1);
    }
    
    std::ifstream j_volume_stream(j_volume.c_str(), std::ifstream::in);
    if (!j_volume_stream.is_open())
    {
        std::cout << "error opening volume file - calcVolumeIntersect" << j_volume << std::endl;
        i_volume_stream.close();
        exit(1);
    }
    std::vector<int> blocks_i;
    std::vector<int> blocks_j;
    std::vector<int> intersect_i_j;
    std::string content;
    std::vector<std::string> splitted_content;


    while (std::getline(i_volume_stream, content))
    {
        splitted_content = split_string(content, ",");
        if (splitted_content[0] == "B")
        {
            blocks_i.push_back(std::stoi(splitted_content[1]));
        }
    }
    i_volume_stream.close();

    while (std::getline(j_volume_stream, content))
    {
        splitted_content = split_string(content, ",");
        if (splitted_content[0] == "B")
        {
            blocks_j.push_back(std::stoi(splitted_content[1]));
        }
    }
    j_volume_stream.close();

    std::set_intersection(blocks_i.begin(), blocks_i.end(), blocks_j.begin(), blocks_j.end(), back_inserter(intersect_i_j));
    return intersect_i_j;
}

std::vector<double> getBlockSizes(std::vector<std::string> source_volume_list, std::vector<std::pair<int, int>> num_of_blocks_and_files_sourceVolumes) 
{
    int max_block_sn = 0;
	for (auto &item : num_of_blocks_and_files_sourceVolumes) {
		max_block_sn += item.first;
	}

    std::vector<double> blockSizes(max_block_sn, 0);
    for (auto &source_volume : source_volume_list) {
        std::ifstream source_volume_stream(source_volume.c_str(), std::ifstream::in);
        if (!source_volume_stream.is_open())
        {
            std::cout << "error opening volume file - getBlockSizes" << source_volume << std::endl;
            exit(1);
        }
        
        std::string content;
        std::vector<std::string> splitted_content;

        while (std::getline(source_volume_stream, content))
        {
            splitted_content = split_string(content, ",");
            if (splitted_content[0] == "F")
            {
                int number_of_blocks_in_file_line = std::stoi(splitted_content[4]);
                for (register int i = 0; i < 2 * number_of_blocks_in_file_line; i += 2) //read block_sn and block_size simultaneously and add constrains to the model.
                {
                    int block_sn = std::stoi(splitted_content[5 + i]);
                    int size_read = std::stoi(splitted_content[6 + i]); //update block size histogram
                    if (blockSizes[block_sn] == 0)
                    {
                        blockSizes[block_sn] = ((double)size_read) / 1024.0;
                    }
                }
            }
        }
        source_volume_stream.close();
	}

    while (!blockSizes.empty() && blockSizes[blockSizes.size() - 1] == 0) {
        blockSizes.pop_back();
    }

    return blockSizes;
}

std::pair<int, int> getLastBlockAndFileSn(std::vector<std::string> source_volume_list) 
{
    int lastBlockSn = 0;
    int lastFileSn = 0;
    for (auto &source_volume : source_volume_list) {
        std::ifstream source_volume_stream(source_volume.c_str(), std::ifstream::in);
        if (!source_volume_stream.is_open())
        {
            std::cout << "error opening volume file - getLastBlockSn" << source_volume << std::endl;
            exit(1);
        }
        
        std::string content;
        std::vector<std::string> splitted_content;

        while (std::getline(source_volume_stream, content))
        {
            splitted_content = split_string(content, ",");
            if (splitted_content[0] == "F")
            {
                lastFileSn = std::max(lastFileSn, std::stoi(splitted_content[1]));
            }
            if (splitted_content[0] == "B")
            {
                lastBlockSn = std::max(lastBlockSn, std::stoi(splitted_content[1]));
            }
        }
        source_volume_stream.close();
	}   
    return std::make_pair(lastBlockSn, lastFileSn);
}

std::vector<std::set<int>> getFileSnInVolumes(std::vector<std::string> source_volume_list)
{
    std::vector<std::set<int>> fileSnInVolume;
    for (int source = 0; source < source_volume_list.size(); source++) {
        std::ifstream source_volume_stream(source_volume_list[source].c_str(), std::ifstream::in);
        if (!source_volume_stream.is_open())
        {
            std::cout << "error opening volume file - addConstraint_DontRemapNonExistantFilesOfRemapToSelf" << source_volume_list[source] << std::endl;
            exit(1);
        }

        std::set<int> fileSnSet;
        fileSnInVolume.push_back(fileSnSet);
        std::string content;
        std::vector<std::string> splitted_content;
        while (std::getline(source_volume_stream, content))
        {
            splitted_content = split_string(content, ",");
            if (splitted_content[0] == "F")
            {
                fileSnInVolume[source].insert(std::stoi(splitted_content[1]));
            }
        }
        source_volume_stream.close();
	}   
    return fileSnInVolume;
}

void addConstraint_allIntersectsAreCopied(GRBModel model, std::vector<std::vector<std::vector<int>>> intersects_source_target_blocksn, std::vector<std::vector<GRBVar*>> C_i_s_t)
{
    int constraintAdded = 0;
    for (int source = 0; source < intersects_source_target_blocksn.size(); source++) {
		for (int target = 0; target < intersects_source_target_blocksn[source].size(); target++) {
            for (int i = 0; i < intersects_source_target_blocksn[source][target].size(); i++) {
                model.addConstr(C_i_s_t[intersects_source_target_blocksn[source][target][i]][source][target], GRB_EQUAL, 1);
            }      
        }
	}
}

void addConstraint_RemapFilesToOnlyOneVolume(GRBModel model, std::vector<std::vector<GRBVar*>> X_l_s_t, std::vector<std::pair<int, int>> num_of_blocks_and_files_sourceVolumes, int numOfTargetVolumes)
{
    for (int l = 0; l < X_l_s_t.size(); l++) {
        for (int source = 0; source < X_l_s_t[l].size(); source ++) {
            GRBLinExpr Sum_X_l_s_t = 0.0;
            for (int target = 0; target < numOfTargetVolumes; target++) {
                Sum_X_l_s_t += X_l_s_t[l][source][target];
            }
            model.addConstr(Sum_X_l_s_t <= 1);  
        }
	}
}

void addConstraint_DontRemapNonExistantFilesOfRemapToSelf(GRBModel model, std::vector<std::vector<GRBVar*>> X_l_s_t, std::vector<std::set<int>> fileSnInVolumes, int numOfTargetVolumes)
{
    for (int l = 0; l < X_l_s_t.size(); l++) {
        for (int source = 0; source < X_l_s_t[l].size(); source ++) {
            model.addConstr(X_l_s_t[l][source][source], GRB_EQUAL, 0 );
            if(fileSnInVolumes[source].count(l) == 1){
                continue;
            } else {
                for (int target = 0; target < numOfTargetVolumes; target++) {
                    model.addConstr(X_l_s_t[l][source][target], GRB_EQUAL, 0 );
                }   
            }
        }
    }
}

void addConstraint_BlockIsDeletedOnlyIfNoLocalFileUsingItRemains(GRBModel model, std::vector<std::vector<GRBVar*>> X_l_s_t, std::vector<GRBVar*> D_i_s, std::vector<std::string> source_volume_list, int numOfTargetVolumes)
{
    for (int source = 0; source < source_volume_list.size(); source++) {
        std::ifstream source_volume_stream(source_volume_list[source].c_str(), std::ifstream::in);
        if (!source_volume_stream.is_open())
        {
            std::cout << "error opening volume file - addConstraint_BlockIsDeletedOnlyIfNoLocalFileUsingItRemains" << source_volume_list[source] << std::endl;
            exit(1);
        }

        std::string content;
        std::vector<std::string> splitted_content;
        while (std::getline(source_volume_stream, content))
        {
            splitted_content = split_string(content, ",");
            if (splitted_content[0] == "F")
            {
                int fileSn = std::stoi(splitted_content[1]);
                int number_of_blocks_in_file_line = std::stoi(splitted_content[4]);
                for (register int i = 0; i < 2 * number_of_blocks_in_file_line; i += 2) //read block_sn and block_size simultaneously and add constrains to the model.
                {
                    int block_sn = std::stoi(splitted_content[5 + i]);
                    GRBLinExpr Sum_X_l_s_t = 0.0;
                    for (int target = 0; target < numOfTargetVolumes; target++) {
                        Sum_X_l_s_t += X_l_s_t[fileSn][source][target];
                    }
                    model.addConstr(D_i_s[block_sn][source] <= Sum_X_l_s_t);
                }
            }
        }
        source_volume_stream.close();
	}   
}

int main(int argc, char *argv[])
{
    const auto begin = std::chrono::high_resolution_clock::now(); //start the stopwatch for the total time.
    if (argc != 14)                                               //very specific argument format for the program.
    {
        std::cout
            << "arguments format is: {volumes} {benchmarks output file name} {T} {MM} {where to write the optimization solution} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {v1_file_system_start} {v2_file_system_end}"
            << std::endl;
        return 0;
    }
    volume_list = std::string(argv[1]);
    benchmarks_file_name = std::string(argv[2]);
    T_percentage = std::stod(std::string(argv[3]));
    MM_percentage = std::stod(std::string(argv[4]));
    std::string write_solution = std::string(argv[5]);
    filter_factor = std::stod(std::string(argv[6]));
    model_time_limit = std::stod(std::string(argv[7]));
    time_limit_option = model_time_limit != 0;
    seed = std::string(argv[8]);
    number_of_threads = std::string(argv[9]);
    average_block_size = std::stod(std::string(argv[10]));
    depth_level = std::string(argv[11]);
    v1_file_system_start = std::string(argv[12]);
    v2_file_system_end = std::string(argv[13]);
    // int num_of_metadata_lines = get_num_of_metadata_lines(input_file_name);
    std::ifstream volume_list_f(volume_list.c_str(), std::ifstream::in);
    if (!volume_list_f.is_open())
    {
        std::cout << "error opening volume list." << std::endl;
        exit(1);
    }
	
    std::string content;
    std::getline(volume_list_f, content);

    std::vector<std::string> source_volume_list;
    std::vector<std::string> target_volume_list;

    while (std::getline(volume_list_f, content)) 
    {
        std::string file_path = content.substr(0, content.find(", "));
        std::string volume_type = content.substr(content.find(", ") + 2);

        if(volume_type.compare("s") || volume_type.compare("a")) {
            source_volume_list.push_back(file_path);
        }
        if(volume_type.compare("t") || volume_type.compare("a")) {
            target_volume_list.push_back(file_path);
        }
    }

    std::vector<std::vector<std::vector<int>>> intersects_source_target_blocksn;
    for (int i = 0; i < source_volume_list.size(); i++) {        
        std::vector<std::vector<int>> intersects_i;
        intersects_source_target_blocksn.push_back(intersects_i);
        for (int j = 0; j < target_volume_list.size(); j++) {
            std::vector<int> intersect_i_j = calcVolumeIntersect(source_volume_list[i], target_volume_list[j]);
            intersects_source_target_blocksn[i].push_back(intersect_i_j);
        }
    }

    std::vector<std::pair<int, int>> num_of_blocks_and_files_sourceVolumes;
    std::vector<std::pair<int, int>> num_of_blocks_and_files_targetVolumes;
    for (int i = 0; i < source_volume_list.size(); i++) {        
        int num_of_metadata_lines = get_num_of_metadata_lines(source_volume_list[i]);
        std::pair<int, int> num_of_blocks_and_files_i = get_num_of_blocks_and_files(source_volume_list[i], num_of_metadata_lines);
        num_of_blocks_and_files_sourceVolumes.push_back(num_of_blocks_and_files_i);
    }
    for (int j = 0; j < target_volume_list.size(); j++) {
        int num_of_metadata_lines = get_num_of_metadata_lines(target_volume_list[j]);
        std::pair<int, int> num_of_blocks_and_files_j = get_num_of_blocks_and_files(target_volume_list[j], num_of_metadata_lines);  
        num_of_blocks_and_files_targetVolumes.push_back(num_of_blocks_and_files_j);
    }

    std::vector<double> block_sizes = getBlockSizes(source_volume_list, num_of_blocks_and_files_sourceVolumes);
    std::pair<int, int> lastSourceSn_block_file = getLastBlockAndFileSn(source_volume_list);
    
    std::vector<std::set<int>> fileSnInVolume = getFileSnInVolumes(source_volume_list);
    // for (int i = 0; i < block_sizes.size(); i++) {
	// 	std::cout << "block " << i << "is " << block_sizes[i] << "MB" << std::endl;  
	// }
    // for (auto &item : num_of_blocks_and_files_targetVolumes) {
	// 	std::cout << "blocks: " << item.first << "files: " << item.second << std::endl;  
	// }

    GRBEnv *env = 0;
    GRBVar *blocks_copied = 0; //Cist
    GRBVar *blocks_deleted = 0; //Dis
    GRBVar *files = 0;  //Xist
    GRBConstr *constrains = 0;
    GRBConstr *constrains_hint = 0;
    bool need_to_free_hint_constrains = false;
    std::vector<GRBLinExpr> left_side;
    std::vector<GRBLinExpr> left_side_hint; //files that does not have blocks should stay at source

    std::vector<std::vector<GRBVar*>> C_i_s_t;
    std::vector<GRBVar*> D_i_s;
    std::vector<std::vector<GRBVar*>> X_l_s_t;

    try
    {
        env = new GRBEnv(); //This may throw if there is no valid licence.
        GRBModel model = GRBModel(*env);
        model.set(GRB_StringAttr_ModelName, "GoSeed");
        if (time_limit_option)
        {
            model.set(GRB_DoubleParam_TimeLimit, model_time_limit); //set time limit
        }

        model.set("Seed", seed.c_str());
        model.set("Threads", number_of_threads.c_str());

        for (int i = 0; i <= lastSourceSn_block_file.first; i++) {
            std::vector<GRBVar*> C_s_t;
            C_i_s_t.push_back(C_s_t);
            for (int source = 0; source < source_volume_list.size(); source++) {
                blocks_copied = model.addVars(target_volume_list.size(), GRB_BINARY);
                blocks_deleted = model.addVars(target_volume_list.size(), GRB_BINARY);
                files = model.addVars(target_volume_list.size(), GRB_BINARY);
                
                C_i_s_t[i].push_back(blocks_copied);
                D_i_s.push_back(blocks_deleted);
            }
        }
        model.update();

        for (int l = 0; l <= lastSourceSn_block_file.second; l++) {
            std::vector<GRBVar*> X_s_t;
            X_l_s_t.push_back(X_s_t);  
            for (int source = 0; source < source_volume_list.size(); source++) {
                files = model.addVars(target_volume_list.size(), GRB_BINARY);
                
                X_l_s_t[l].push_back(files);
            }
        }
        model.update();
        
        addConstraint_allIntersectsAreCopied(model, intersects_source_target_blocksn, C_i_s_t);
        model.update();
        addConstraint_RemapFilesToOnlyOneVolume(model, X_l_s_t, num_of_blocks_and_files_sourceVolumes, target_volume_list.size());
        model.update();
        addConstraint_DontRemapNonExistantFilesOfRemapToSelf(model, X_l_s_t, fileSnInVolume, target_volume_list.size());
        model.update();
        addConstraint_BlockIsDeletedOnlyIfNoLocalFileUsingItRemains(model, X_l_s_t, D_i_s, source_volume_list, target_volume_list.size());
        model.update();

        model.write("debud.lp");
        std::cout << "AAAAAAAAAAAAAAAAAAAA";

    } catch(GRBException e) {
        std::cout << "Error code = " << e.getErrorCode() << std::endl;
        std::cout << e.getMessage() << std::endl;
    } catch(...) {
        std::cout << "Exception during optimization" << std::endl;
    }





    //     int file_sn;
    //     int block_sn;
    //     int number_of_blocks_in_file_line;
    //     std::string content;
    //     int size_read;
    //     std::vector<std::string> splitted_content;
    //     intersect_block_number = 0;
    //     while (std::getline(f, content))
    //     {
    //         splitted_content = split_string(content, ",");
    //         if (splitted_content[0] == "F")
    //         {
    //             file_sn = std::stoi(std::stoi(splitted_content[1]);)
    //             //skip file_id its useless
    //             //skip dir_sn its useless
    //             number_of_blocks_in_file_line = std::stoi(splitted_content[4]);
    //             for (register int i = 0; i < 2 * number_of_blocks_in_file_line; i += 2) //read block_sn and block_size simultaneously and add constrains to the model.
    //             {
    //                 block_sn = std::stoi(splitted_content[5 + i]);
    //                 size_read = std::stoi(splitted_content[6 + i]); //update block size histogram
    //                 if (block_size[block_sn] == 0)
    //                 {
    //                     block_size[block_sn] = ((double)size_read) / 1024.0;
    //                 }
    //                 left_side.push_back(blocks_migrated[block_sn] - files[file_sn]);
    //                 left_side.push_back(files[file_sn] - blocks_migrated[block_sn] - blocks_replicated[block_sn]);
    //             }
    //             if (number_of_blocks_in_file_line == 0)
    //             {
    //                 left_side_hint.push_back(files[file_sn]);
    //             }
    //         }
    //         else if (splitted_content[0] == "B")
    //         {
    //             //disjoinCheck
    //             if( hashmap.find(std::string(splitted_content[2])) == hashmap.end() ) {
    //                 blocks_is_in_intersect.push_back(false);
    //             } else {
    //                 intersect_block_number++;
    //                 blocks_is_in_intersect.push_back(true);
    //             }
                
    //             GRBLinExpr no_orphans = 0.0;
    //             block_sn = std::stoi(std::stoi(splitted_content[1]);)
    //             //skip block_id its useless
    //             number_of_blocks_in_file_line = std::stoi(splitted_content[3]); //number of files in line reusing number_of_blocks_in_file_line for convenient
    //             no_orphans = no_orphans + blocks_replicated[block_sn] - number_of_blocks_in_file_line;
    //             for (int i = 0; i < number_of_blocks_in_file_line; i++) //read block_sn and block_size simultaneously and add constrains to the model.
    //             {
    //                 file_sn = std::stoi(splitted_content[4 + i]);
    //                 no_orphans += files[file_sn];
    //             }
    //             left_side.push_back(no_orphans);
    //         }
    //         else
    //         {
    //             break; // skip dirs and roots information
    //         }
    //     }
    //     f.close();
    //     std::cout << "done reading the file" << std::endl;

    //     //add the constrains to the model
    //     std::vector<double> right_side;
    //     std::vector<double> right_side_hint;
    //     std::vector<std::string> names;
    //     std::vector<std::string> names_hint;
    //     std::vector<char> senses;
    //     std::vector<char> senses_hint;
    //     names.assign(left_side.size(), "");
    //     names_hint.assign(left_side_hint.size(), "");
    //     right_side.assign(left_side.size(), 0.0);
    //     right_side_hint.assign(left_side_hint.size(), 0.0);
    //     senses.assign(left_side.size(), GRB_LESS_EQUAL);
    //     senses_hint.assign(left_side_hint.size(), GRB_EQUAL);

    //     constrains = model.addConstrs(&left_side[0], &senses[0], &right_side[0], &names[0], (int)left_side.size());

    //     if ((int)left_side_hint.size() != 0) //found at least one empty file.
    //     {
    //         constrains_hint = model.addConstrs(&left_side_hint[0], &senses_hint[0], &right_side_hint[0], &names_hint[0], (int)left_side_hint.size());
    //         need_to_free_hint_constrains = true;
    //     }

    //     left_side.clear();
    //     left_side_hint.clear();
    //     right_side.clear();
    //     right_side_hint.clear();
    //     names.clear();
    //     names_hint.clear();
    //     senses.clear();
    //     senses_hint.clear();

    //     //done adding to model the constrains
    //     GRBLinExpr all_migrated_blocks = 0.0;
    //     GRBLinExpr all_replicated_blocks = 0.0;
    //     GRBLinExpr totalTraffic = 0.0;
    //     GRBLinExpr totalClean = 0.0;
    //     GRBLinExpr totalAdd = 0.0;
    //     GRBLinExpr totalVolume = 0.0;

    //     for (int i = 0; i < num_of_blocks; i++)
    //     {
    //         all_migrated_blocks += blocks_migrated[i] * block_size[i];
    //         all_replicated_blocks += blocks_replicated[i] * block_size[i];
    //         if( !blocks_is_in_intersect[i] ) {
    //             totalTraffic += blocks_migrated[i] * block_size[i] + blocks_replicated[i] * block_size[i];
    //             totalAdd += blocks_replicated[i] * block_size[i];
    //         } else {
    //             totalClean += blocks_migrated[i] * block_size[i];
    //         }
    //         total_block_size_Kbytes += block_size[i];
    //     }
    //     totalVolume = totalAdd - totalClean;
    //     T_Kbytes = total_block_size_Kbytes * T_percentage / 100;                //assign the number of bytes to migrate
    //     epsilon_Kbytes = total_block_size_Kbytes * MM_percentage / 100;    //assign the epsilon in bytes.

    //     std::cout << MM_percentage << " percent is " << epsilon_Kbytes << std::endl;

    //     model.addConstr(totalTraffic <= T_Kbytes);                              // shouldn't pass more than M bytes
    //     model.addConstr(all_migrated_blocks >= epsilon_Kbytes);                 // shouldn't pass less than epsilon bytes
    //     model.setObjective(totalVolume, GRB_MINIMIZE);                          //minimize the impact we have on the total volume.

    //     save_block_size_array(block_size);
    //     delete[] block_size;
    //     std::cout << "start optimize now..." << std::endl;
    //     auto s1 = std::chrono::high_resolution_clock::now();
    //     // model.update();
    //     // model.write("debud.lp");
        
    //     model.optimize();
        
    //     double solver_time = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - s1).count();

    //     variable_number = model.get(GRB_IntAttr_NumVars);
    //     constraint_number = model.get(GRB_IntAttr_NumConstrs);

    //     block_size = new double[num_of_blocks];
    //     load_block_size_array_and_del_temp_file(block_size);

    //     int status = model.get(GRB_IntAttr_Status);
    //     if (status == GRB_OPTIMAL)
    //     {
    //         solution_status = "OPTIMAL";
    //     }
    //     if (status == GRB_INFEASIBLE)
    //     {
    //         solution_status = "INFEASIBLE";
    //     }
    //     if (status == GRB_TIME_LIMIT)
    //     {
    //         solution_status = "TIME_LIMIT";
    //     }
    //     std::cout << "done optimization" << std::endl
    //               << std::flush;
    //     if (solution_status != "INFEASIBLE")
    //     {
    //         // Kbytes_to_replicate = model.get(GRB_DoubleAttr_ObjVal);
    //         Kbytes_to_replicate = actual_R_Kbytes;

    //         //print the results.
    //         try
    //         {
    //             calculate_migration_and_save_solution(blocks_migrated, blocks_replicated, blocks_is_in_intersect, files, write_solution, block_size);
    //         }
    //         catch (...)
    //         {
    //             std::cout << "Exception at print_results, probably can't read variables" << std::endl;
    //             solution_status = "TIME_LIMIT_AT_PRESOLVE";
    //         }
    //     }
    //     delete[] block_size;
    //     double elapsed_secs = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - begin).count();
    //     save_statistics(elapsed_secs, solver_time);
    // }
    // catch (...)
    // {
    //     std::cout << "Exception during optimization" << std::endl;
    // }
    // delete[] constrains;
    // if (need_to_free_hint_constrains)
    // {
    //     delete[] constrains_hint;
    // }
    // delete[] blocks_migrated;
    // delete[] blocks_replicated;
    // delete[] files;
    // delete env;
    // return 0;
}