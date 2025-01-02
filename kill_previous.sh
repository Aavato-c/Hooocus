PATH_OF_PID_FILE="__cache__/pids.txt"

# Kill all previous processes
echo "Kill all previous processes"
if [ -f $PATH_OF_PID_FILE ]; then
    while read line; do
        kill -9 $line
        echo "Killed process with PID: $line"
    done < $PATH_OF_PID_FILE
fi
echo "All previous processes are killed"

# Remove the file
rm -f $PATH_OF_PID_FILE
echo "Removed the file: $PATH_OF_PID_FILE"
