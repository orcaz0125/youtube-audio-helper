// SPDX-License-Identifier: GPL-3.0-or-later
// Native Messaging launcher for Windows. Inherits Chrome's binary pipes and
// directly launches Python, avoiding cmd.exe and quoting/code-page problems.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string>
#include <vector>
#include <cstdio>
int wmain() {
    std::vector<wchar_t> executable(32768);
    const DWORD length=GetModuleFileNameW(nullptr,executable.data(),static_cast<DWORD>(executable.size()));
    if(!length||length>=executable.size())return 2;
    std::wstring host(executable.data(),length);
    host.resize(host.find_last_of(L"\\/")); // bin
    host.resize(host.find_last_of(L"\\/")); // host
    const std::wstring python=host+L"\\.venv\\Scripts\\python.exe";
    const std::wstring script=host+L"\\native_host.py";
    const std::wstring log=host+L"\\native.log";
    if(GetFileAttributesW(python.c_str())==INVALID_FILE_ATTRIBUTES)return 3;
    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES),nullptr,TRUE};
    HANDLE error=CreateFileW(log.c_str(),FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,&security,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(error==INVALID_HANDLE_VALUE)return 4;
    STARTUPINFOW startup{};startup.cb=sizeof(startup);startup.dwFlags=STARTF_USESTDHANDLES;
    startup.hStdInput=GetStdHandle(STD_INPUT_HANDLE);startup.hStdOutput=GetStdHandle(STD_OUTPUT_HANDLE);startup.hStdError=error;
    SetHandleInformation(startup.hStdInput,HANDLE_FLAG_INHERIT,HANDLE_FLAG_INHERIT);
    SetHandleInformation(startup.hStdOutput,HANDLE_FLAG_INHERIT,HANDLE_FLAG_INHERIT);
    PROCESS_INFORMATION child{};
    std::wstring command=L"\""+python+L"\" -u \""+script+L"\"";
    const BOOL started=CreateProcessW(python.c_str(),&command[0],nullptr,nullptr,TRUE,CREATE_NO_WINDOW,nullptr,host.c_str(),&startup,&child);
    if(!started){DWORD code=GetLastError();std::string message="Python launch failed: "+std::to_string(code)+"\n";DWORD written=0;WriteFile(error,message.data(),static_cast<DWORD>(message.size()),&written,nullptr);CloseHandle(error);return 5;}
    CloseHandle(child.hThread);WaitForSingleObject(child.hProcess,INFINITE);
    DWORD result=1;GetExitCodeProcess(child.hProcess,&result);CloseHandle(child.hProcess);CloseHandle(error);
    return static_cast<int>(result);
}
