using System;
using System.IO;
using System.Net;
using System.Drawing;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Collections.Generic;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

static class Program {
    internal static readonly string Root=AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
    internal static readonly string Url="http://127.0.0.1:8791";
    [System.Runtime.InteropServices.DllImport("user32.dll",CharSet=System.Runtime.InteropServices.CharSet.Unicode)] static extern IntPtr FindWindow(string cls,string title);
    [System.Runtime.InteropServices.DllImport("user32.dll")] static extern bool ShowWindow(IntPtr handle,int command);
    [System.Runtime.InteropServices.DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr handle);
    internal static bool Smoke;
    [STAThread] static void Main(string[] args) {
        Smoke=Array.IndexOf(args,"--smoke")>=0;
        bool first; using(var mutex=new Mutex(true,"Local\\OmniDispatch-Desktop-"+Root.GetHashCode().ToString("X"),out first)) {
            if(!first && !Smoke) {var existing=FindWindow(null,"OmniDispatch · 发布从这里生长");if(existing!=IntPtr.Zero){ShowWindow(existing,9);SetForegroundWindow(existing);}return;}
            Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainWindow());
        }
    }
    internal static Process Python(string module,string arguments) {
        var exe=Path.Combine(Root,"runtime","pythonw.exe");
        if(!File.Exists(exe))throw new IOException("缺少内置运行环境。请完整解压运行包。");
        var info=new ProcessStartInfo(exe,"-m "+module+" "+arguments){WorkingDirectory=Root,UseShellExecute=false,CreateNoWindow=true};
        info.EnvironmentVariables["PYTHONUTF8"]="1";
        return Process.Start(info);
    }
}
class MainWindow:Form {
    WebView2 view; Label status; NotifyIcon tray; bool exiting; bool ready;
    readonly string diagnostics=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"OmniDispatch","Diagnostics");
    void TraceStep(string step){try{Directory.CreateDirectory(diagnostics);File.AppendAllText(Path.Combine(diagnostics,"startup.log"),DateTime.UtcNow.ToString("o")+" "+step+Environment.NewLine);}catch{}}
    readonly JavaScriptSerializer json=new JavaScriptSerializer();
    readonly HashSet<string> logins=new HashSet<string>();
    public MainWindow() {
        Text="OmniDispatch · 发布从这里生长";Size=new Size(1420,920);MinimumSize=new Size(900,640);
        StartPosition=FormStartPosition.CenterScreen;BackColor=Color.FromArgb(255,249,245);
        Icon=SystemIcons.Application;
        var icon=Path.Combine(Program.Root,"desktop","omnidispatch.ico");if(File.Exists(icon))Icon=new Icon(icon);
        status=new Label{Dock=DockStyle.Fill,Text="正在唤醒本机工作台…",TextAlign=ContentAlignment.MiddleCenter,Font=new Font("Microsoft YaHei UI",14),ForeColor=Color.FromArgb(43,26,23)};Controls.Add(status);
        tray=new NotifyIcon{Icon=Icon,Text="OmniDispatch · 本机发布工作台",Visible=!Program.Smoke};
        var menu=new ContextMenuStrip();menu.Items.Add("打开工作台",null,(s,e)=>Restore());menu.Items.Add("打开本机目录",null,(s,e)=>Process.Start("explorer.exe",Program.Root));
        menu.Items.Add("退出桌面窗口（后台继续）",null,(s,e)=>{exiting=true;Close();});tray.ContextMenuStrip=menu;tray.DoubleClick+=(s,e)=>Restore();
        Shown+=async(s,e)=>await Boot();
        FormClosing+=(s,e)=>{if(!exiting&&!Program.Smoke){e.Cancel=true;Hide();tray.ShowBalloonTip(2000,"OmniDispatch","已收进托盘，本机定时任务继续运行。",ToolTipIcon.Info);}};
        FormClosed+=(s,e)=>{tray.Dispose();if(view!=null)view.Dispose();};
    }
    void Restore(){Show();WindowState=FormWindowState.Normal;Activate();}
    void RuntimeReadPermissions(string folder){
        if(!Directory.Exists(folder))return;
        var access=Directory.GetAccessControl(folder);bool changed=false;
        foreach(string sid in new[]{"S-1-15-2-1","S-1-15-2-2"}){
            var identity=new System.Security.Principal.SecurityIdentifier(sid);
            var rule=new System.Security.AccessControl.FileSystemAccessRule(identity,System.Security.AccessControl.FileSystemRights.ReadAndExecute,System.Security.AccessControl.InheritanceFlags.ContainerInherit|System.Security.AccessControl.InheritanceFlags.ObjectInherit,System.Security.AccessControl.PropagationFlags.None,System.Security.AccessControl.AccessControlType.Allow);
            access.AddAccessRule(rule);changed=true;
        }
        if(changed)Directory.SetAccessControl(folder,access);
    }
    async Task<bool> Healthy(){return await Task.Run(()=>{try{var r=(HttpWebRequest)WebRequest.Create(Program.Url+"/api/health");r.Timeout=1500;r.Proxy=null;using(var response=r.GetResponse())using(var reader=new StreamReader(response.GetResponseStream()))return reader.ReadToEnd().Contains("omnidispatch");}catch{return false;}});}
    async Task Boot() {
        try {
            TraceStep("boot");
            if(!await Healthy()) {
                Program.Python("omnidispatch.desktop_runtime","");
                for(int i=0;i<60&&!await Healthy();i++)await Task.Delay(1000);
            }
            if(!await Healthy())throw new Exception("本机服务未启动。请查看 logs 或 state\\supervisor.log 后重试。");
            TraceStep("service-ready");
            if(view!=null){Controls.Remove(view);view.Dispose();view=null;}
            view=new WebView2{Dock=DockStyle.Fill,DefaultBackgroundColor=BackColor};Controls.Add(view);view.BringToFront();
            var profile=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"OmniDispatch","WebView2");
            var bundled=Path.Combine(Program.Root,"desktop","webview2-runtime");
            try{RuntimeReadPermissions(bundled);}catch(UnauthorizedAccessException){TraceStep("runtime-acl-already-managed");}
            TraceStep("browser-environment");
            var env=await CoreWebView2Environment.CreateAsync(File.Exists(Path.Combine(bundled,"msedgewebview2.exe"))?bundled:null,profile);
            TraceStep("browser-initialize");
            var initialize=view.EnsureCoreWebView2Async(env);
            if(await Task.WhenAny(initialize,Task.Delay(30000))!=initialize)throw new Exception("浏览器窗口初始化超时");
            await initialize;TraceStep("browser-ready");
            var core=view.CoreWebView2;core.Settings.AreDevToolsEnabled=!Program.Smoke;core.Settings.AreDefaultContextMenusEnabled=false;core.Settings.IsStatusBarEnabled=false;
            core.Settings.IsGeneralAutofillEnabled=false;core.Settings.IsPasswordAutosaveEnabled=false;
            core.NavigationStarting+=(s,e)=>{Uri u;if(!Uri.TryCreate(e.Uri,UriKind.Absolute,out u)||u.GetLeftPart(UriPartial.Authority)!=Program.Url){e.Cancel=true;if(u!=null&&u.Scheme=="https")Process.Start(new ProcessStartInfo(e.Uri){UseShellExecute=true});}};
            core.NewWindowRequested+=(s,e)=>{e.Handled=true;Uri u;if(Uri.TryCreate(e.Uri,UriKind.Absolute,out u)&&u.Scheme=="https")Process.Start(new ProcessStartInfo(e.Uri){UseShellExecute=true});};
            core.PermissionRequested+=(s,e)=>e.State=CoreWebView2PermissionState.Deny;
            core.WebMessageReceived+=Message;
            core.NavigationCompleted+=async(s,e)=>{
                if(!e.IsSuccess){status.Text="本机工作台暂未响应，请从托盘重新打开。";return;}
                ready=true;TraceStep("page-loaded");
                if(Program.Smoke){try{await Task.Delay(4500);await CaptureCheck();}catch(Exception error){TraceStep("capture-failed:"+error.Message);WriteCheck(false,error.Message);}exiting=true;Close();}
            };
            TraceStep("navigate");
            core.Navigate(Program.Url+"/?desktop=1");
        } catch(Exception e) {
            TraceStep("failed:"+e.GetType().Name+":"+e.Message);
            status.BringToFront();status.Text="启动未完成\n"+e.Message+"\n点击此处重试";status.Click+=async(s,a)=>await Boot();
            if(Program.Smoke){WriteCheck(false,e.GetType().Name);exiting=true;Close();}
        }
    }
    async void Message(object sender,CoreWebView2WebMessageReceivedEventArgs e) {
        string pending=null;
        try {
            Uri source;if(!Uri.TryCreate(e.Source,UriKind.Absolute,out source)||source.GetLeftPart(UriPartial.Authority)!=Program.Url)return;
            var data=json.Deserialize<Dictionary<string,object>>(e.WebMessageAsJson);
            if(!data.ContainsKey("type"))return;
            if(Convert.ToString(data["type"])=="browser-job"){
                string job=Convert.ToString(data["job"]);if(!Regex.IsMatch(job,"^[a-f0-9-]{36}$"))return;
                if(logins.Contains(job))return;pending=job;logins.Add(job);
                var worker=Program.Python("omnidispatch.browser_desktop","job --job "+job);
                await Task.Run(()=>worker.WaitForExit());worker.Dispose();view.CoreWebView2.PostWebMessageAsJson("{\"type\":\"browser-job-finished\"}");return;
            }
            if(Convert.ToString(data["type"])!="login")return;
            string channel=Convert.ToString(data["channel"]),account=Convert.ToString(data["account"]);
            if(!Regex.IsMatch(channel,"^[a-z0-9-]{1,80}$")||!Regex.IsMatch(account,"^[a-f0-9-]{36}$"))return;
            string key=channel+":"+account;if(logins.Contains(key))return;logins.Add(key);pending=key;
            bool browserLogin=data.ContainsKey("engine")&&(Convert.ToString(data["engine"])=="desktopweb"||Convert.ToString(data["engine"])=="sau");
            var process=browserLogin?Program.Python("omnidispatch.browser_desktop","login --channel "+channel+" --account "+account):Program.Python("omnidispatch.desktop_login","--state \""+Path.Combine(Program.Root,"state")+"\" --channel "+channel+" --account "+account);
            await Task.Run(()=>process.WaitForExit());int exitCode=process.ExitCode;logins.Remove(key);process.Dispose();
            view.CoreWebView2.PostWebMessageAsJson(json.Serialize(new{type=exitCode==0?"login-finished":"login-error",channel=channel,account=account}));
        }catch(Exception){if(view!=null&&ready)view.CoreWebView2.PostWebMessageAsJson("{\"type\":\"login-error\"}");}
        finally{if(pending!=null)logins.Remove(pending);}
    }
    async Task CaptureCheck(){
        Directory.CreateDirectory(diagnostics);
        await view.CoreWebView2.ExecuteScriptAsync("window.__desktopErrors=[];window.addEventListener('error',e=>window.__desktopErrors.push(e.message));window.addEventListener('unhandledrejection',e=>window.__desktopErrors.push(String(e.reason)));window.__desktopRoutes=[];");
        foreach(var route in new[]{"#/jobs","#/accounts","#/assets","#/agents","#/updates","#/audit","#/settings","#/c/biliup-bilibili","#/?group=short","#/?group=long","#/?group=community","#/?group=writing","#/?group=core"}){
            await view.CoreWebView2.ExecuteScriptAsync("location.hash="+json.Serialize(route));await Task.Delay(1400);
            await view.CoreWebView2.ExecuteScriptAsync("window.__desktopRoutes.push({route:location.hash,controls:document.querySelectorAll('#page input,#page select,#page button').length,text:document.querySelector('#page').innerText.slice(0,90)});");
        }
        var value=await view.CoreWebView2.ExecuteScriptAsync("JSON.stringify({errors:window.__desktopErrors,routes:window.__desktopRoutes,title:document.title,leaves:document.querySelectorAll('.leaf').length,body:document.body.innerText.slice(0,160),width:innerWidth,height:innerHeight,scroll:document.documentElement.scrollHeight})");
        using(var stream=File.Create(Path.Combine(diagnostics,"desktop-preview.png")))await view.CoreWebView2.CapturePreviewAsync(CoreWebView2CapturePreviewImageFormat.Png,stream);
        WriteCheck(true,value);
    }
    void WriteCheck(bool success,string info){Directory.CreateDirectory(diagnostics);File.WriteAllText(Path.Combine(diagnostics,"desktop-check.json"),json.Serialize(new{success=success,webview=CoreWebView2Environment.GetAvailableBrowserVersionString(),detail=info,at=DateTime.UtcNow.ToString("o")}));}
}
